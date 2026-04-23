from __future__ import annotations

import csv
import io
import json
import os
from datetime import time
from typing import Any, Dict, List

import psycopg2
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from timetable_generator.timetable_generator import generate_timetable as run_engine

app = FastAPI(title="Timetable Generator API", version="1.0.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


def get_connection():
	return psycopg2.connect(
		dbname=os.getenv("DB_NAME", "timetable_db"),
		user=os.getenv("DB_USER", "postgres"),
		password=os.getenv("DB_PASSWORD", "123"),
		host=os.getenv("DB_HOST", "localhost"),
		port=os.getenv("DB_PORT", "5432"),
	)


def clear_schedule() -> None:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM timetable;")
			cur.execute("DELETE FROM conflicts;")
		conn.commit()


def get_counts() -> Dict[str, int]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT COUNT(*) FROM timetable;")
			timetable_count = cur.fetchone()[0]
			cur.execute("SELECT COUNT(*) FROM conflicts;")
			conflict_count = cur.fetchone()[0]
	return {
		"timetable_count": timetable_count,
		"conflict_count": conflict_count,
	}


class FacultyCreate(BaseModel):
	name: str = Field(min_length=1)
	department: str | None = None
	email: str | None = None
	assigned_courses: List[int] | None = None


class CourseCreate(BaseModel):
	name: str = Field(min_length=1)
	code: str | None = None
	lectures_per_week: int = Field(gt=0)
	is_lab: bool = False
	duration_hours: float = 1.0


class BatchCreate(BaseModel):
	name: str = Field(min_length=1)
	size: int = Field(gt=0)
	semester: int = Field(ge=1)
	courses: List[int] | None = None


class RoomCreate(BaseModel):
	name: str = Field(min_length=1)
	room_number: str | None = None
	building: str | None = None
	capacity: int = Field(gt=0)
	is_lab: bool = False


class TimeSlotCreate(BaseModel):
	day: str = Field(min_length=1)
	start_time: time
	end_time: time


class AvailabilityItem(BaseModel):
	faculty_id: int = Field(gt=0)
	timeslot_id: int = Field(gt=0)


class AvailabilityCreate(BaseModel):
	items: List[AvailabilityItem]


class ConstraintsPayload(BaseModel):
	course_faculty_map: Dict[int, int] | None = None
	batch_course_map: Dict[int, List[int]] | None = None
	rules: Dict[str, Any] | None = None


class UpdatePayload(BaseModel):
	entity: str = Field(min_length=1)
	id: int = Field(gt=0)
	data: Dict[str, Any]


@app.get("/health")
def health_check() -> Dict[str, str]:
	return {"status": "ok"}


@app.post("/faculty")
def create_faculty(payload: FacultyCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO faculty (name, department, email)
				VALUES (%s, %s, %s)
				RETURNING id;
				""",
				(
					payload.name.strip(),
					(payload.department or "").strip() or None,
					(payload.email or "").strip() or None,
				),
			)
			new_id = cur.fetchone()[0]
			if payload.assigned_courses:
				_merge_faculty_courses(cur, new_id, payload.assigned_courses)
	return {"id": new_id}


@app.post("/course")
def create_course(payload: CourseCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO course (name, code, lectures_per_week, is_lab, duration_hours)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING id;
				""",
				(
					payload.name.strip(),
					(payload.code or "").strip() or None,
					payload.lectures_per_week,
					payload.is_lab,
					payload.duration_hours,
				),
			)
			new_id = cur.fetchone()[0]
	return {"id": new_id}


@app.post("/batch")
def create_batch(payload: BatchCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"INSERT INTO batch (name, size, semester) VALUES (%s, %s, %s) RETURNING id;",
				(payload.name.strip(), payload.size, payload.semester),
			)
			new_id = cur.fetchone()[0]
			if payload.courses:
				_merge_batch_courses(cur, new_id, payload.courses)
	return {"id": new_id}


@app.post("/room")
def create_room(payload: RoomCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO room (name, room_number, building, capacity, is_lab)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING id;
				""",
				(
					payload.name.strip(),
					(payload.room_number or "").strip() or None,
					(payload.building or "").strip() or None,
					payload.capacity,
					payload.is_lab,
				),
			)
			new_id = cur.fetchone()[0]
	return {"id": new_id}


@app.post("/timeslot")
def create_timeslot(payload: TimeSlotCreate) -> Dict[str, Any]:
	if payload.start_time >= payload.end_time:
		raise HTTPException(status_code=400, detail="start_time must be before end_time")
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO timeslot (day, start_time, end_time)
				VALUES (%s, %s, %s)
				RETURNING id;
				""",
				(payload.day.strip(), payload.start_time, payload.end_time),
			)
			new_id = cur.fetchone()[0]
	return {"id": new_id}


@app.get("/faculty")
def list_faculty() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT id, name, department, email FROM faculty ORDER BY id;")
			rows = cur.fetchall()
			availability: Dict[int, List[int]] = {}
			cur.execute("SELECT faculty_id, timeslot_id FROM faculty_availability;")
			for fid, tsid in cur.fetchall():
				availability.setdefault(fid, []).append(tsid)
			course_map = _load_constraint_map(cur, "course_faculty_map")
			assigned: Dict[int, List[int]] = {}
			for course_id, fid in course_map.items():
				try:
					assigned.setdefault(int(fid), []).append(int(course_id))
				except (TypeError, ValueError):
					continue

	items = [
		{
			"id": r[0],
			"name": r[1],
			"department": r[2] or "",
			"email": r[3] or "",
			"available_slots": availability.get(r[0], []),
			"assigned_courses": assigned.get(r[0], []),
		}
		for r in rows
	]
	return {"items": items}


@app.get("/course")
def list_courses() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT id, name, code, lectures_per_week, is_lab, duration_hours
				FROM course
				ORDER BY id;
				"""
			)
			rows = cur.fetchall()
	items = [
		{
			"id": r[0],
			"name": r[1],
			"code": r[2] or "",
			"lectures_per_week": r[3],
			"is_lab": bool(r[4]),
			"duration_hours": float(r[5]) if r[5] is not None else 1.0,
		}
		for r in rows
	]
	return {"items": items}


@app.get("/batch")
def list_batches() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT id, name, size, semester FROM batch ORDER BY id;")
			rows = cur.fetchall()
			batch_map = _load_constraint_map(cur, "batch_course_map")
	items = [
		{
			"id": r[0],
			"name": r[1],
			"size": r[2],
			"semester": r[3] or 1,
			"courses": [int(cid) for cid in batch_map.get(str(r[0]), [])],
		}
		for r in rows
	]
	return {"items": items}


@app.get("/room")
def list_rooms() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT id, name, room_number, building, capacity, is_lab
				FROM room
				ORDER BY id;
				"""
			)
			rows = cur.fetchall()
	items = [
		{
			"id": r[0],
			"name": r[1],
			"room_number": r[2] or r[1],
			"building": r[3] or "",
			"capacity": r[4],
			"is_lab": bool(r[5]),
		}
		for r in rows
	]
	return {"items": items}


@app.get("/timeslot")
def list_timeslots() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT id, day, start_time, end_time
				FROM timeslot
				ORDER BY id;
				"""
			)
			rows = cur.fetchall()
	items = [
		{
			"id": r[0],
			"day": r[1],
			"start_time": r[2].strftime("%H:%M"),
			"end_time": r[3].strftime("%H:%M"),
		}
		for r in rows
	]
	return {"items": items}


@app.put("/faculty/{faculty_id}")
def update_faculty(faculty_id: int, payload: FacultyCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE faculty
				SET name=%s, department=%s, email=%s
				WHERE id=%s;
				""",
				(
					payload.name.strip(),
					(payload.department or "").strip() or None,
					(payload.email or "").strip() or None,
					faculty_id,
				),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
			if payload.assigned_courses:
				_merge_faculty_courses(cur, faculty_id, payload.assigned_courses)
		conn.commit()
	return {"updated": faculty_id}


@app.put("/course/{course_id}")
def update_course(course_id: int, payload: CourseCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE course
				SET name=%s, code=%s, lectures_per_week=%s, is_lab=%s, duration_hours=%s
				WHERE id=%s;
				""",
				(
					payload.name.strip(),
					(payload.code or "").strip() or None,
					payload.lectures_per_week,
					payload.is_lab,
					payload.duration_hours,
					course_id,
				),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"updated": course_id}


@app.put("/batch/{batch_id}")
def update_batch(batch_id: int, payload: BatchCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE batch
				SET name=%s, size=%s, semester=%s
				WHERE id=%s;
				""",
				(payload.name.strip(), payload.size, payload.semester, batch_id),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
			if payload.courses is not None:
				_merge_batch_courses(cur, batch_id, payload.courses)
		conn.commit()
	return {"updated": batch_id}


@app.put("/room/{room_id}")
def update_room(room_id: int, payload: RoomCreate) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE room
				SET name=%s, room_number=%s, building=%s, capacity=%s, is_lab=%s
				WHERE id=%s;
				""",
				(
					payload.name.strip(),
					(payload.room_number or "").strip() or None,
					(payload.building or "").strip() or None,
					payload.capacity,
					payload.is_lab,
					room_id,
				),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"updated": room_id}


@app.put("/timeslot/{timeslot_id}")
def update_timeslot(timeslot_id: int, payload: TimeSlotCreate) -> Dict[str, Any]:
	if payload.start_time >= payload.end_time:
		raise HTTPException(status_code=400, detail="start_time must be before end_time")
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				UPDATE timeslot
				SET day=%s, start_time=%s, end_time=%s
				WHERE id=%s;
				""",
				(payload.day.strip(), payload.start_time, payload.end_time, timeslot_id),
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"updated": timeslot_id}


@app.delete("/faculty/{faculty_id}")
def delete_faculty(faculty_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM faculty WHERE id=%s;", (faculty_id,))
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"deleted": faculty_id}


@app.delete("/course/{course_id}")
def delete_course(course_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM course WHERE id=%s;", (course_id,))
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"deleted": course_id}


@app.delete("/batch/{batch_id}")
def delete_batch(batch_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM batch WHERE id=%s;", (batch_id,))
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"deleted": batch_id}


@app.delete("/room/{room_id}")
def delete_room(room_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM room WHERE id=%s;", (room_id,))
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"deleted": room_id}


@app.delete("/timeslot/{timeslot_id}")
def delete_timeslot(timeslot_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM timeslot WHERE id=%s;", (timeslot_id,))
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()
	return {"deleted": timeslot_id}


@app.post("/availability")
def create_availability(payload: AvailabilityCreate) -> Dict[str, Any]:
	if not payload.items:
		raise HTTPException(status_code=400, detail="items cannot be empty")
	with get_connection() as conn:
		with conn.cursor() as cur:
			for item in payload.items:
				cur.execute(
					"""
					INSERT INTO faculty_availability (faculty_id, timeslot_id)
					VALUES (%s, %s)
					ON CONFLICT DO NOTHING;
					""",
					(item.faculty_id, item.timeslot_id),
				)
		conn.commit()
	return {"inserted": len(payload.items)}


@app.put("/availability/{faculty_id}")
def replace_availability(faculty_id: int, slot_ids: List[int]) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("DELETE FROM faculty_availability WHERE faculty_id=%s;", (faculty_id,))
			for slot_id in slot_ids:
				cur.execute(
					"""
					INSERT INTO faculty_availability (faculty_id, timeslot_id)
					VALUES (%s, %s)
					ON CONFLICT DO NOTHING;
					""",
					(faculty_id, slot_id),
				)
		conn.commit()
	return {"updated": faculty_id, "count": len(slot_ids)}


def upsert_constraint(cur, name: str, value: str) -> None:
	cur.execute("DELETE FROM constraint_rules WHERE name=%s;", (name,))
	cur.execute(
		"INSERT INTO constraint_rules (name, value) VALUES (%s, %s);",
		(name, value),
	)


def _load_constraint_map(cur, name: str) -> Dict[str, Any]:
	cur.execute("SELECT value FROM constraint_rules WHERE name=%s;", (name,))
	row = cur.fetchone()
	if not row or not row[0]:
		return {}
	try:
		data = json.loads(row[0])
		if isinstance(data, dict):
			return data
	except json.JSONDecodeError:
		return {}
	return {}


def _save_constraint_map(cur, name: str, mapping: Dict[str, Any]) -> None:
	upsert_constraint(cur, name, json.dumps(mapping))


def _merge_batch_courses(cur, batch_id: int, course_ids: List[int]) -> None:
	mapping = _load_constraint_map(cur, "batch_course_map")
	mapping[str(batch_id)] = course_ids
	_save_constraint_map(cur, "batch_course_map", mapping)


def _merge_faculty_courses(cur, faculty_id: int, course_ids: List[int]) -> None:
	mapping = _load_constraint_map(cur, "course_faculty_map")
	for cid in course_ids:
		mapping[str(cid)] = faculty_id
	_save_constraint_map(cur, "course_faculty_map", mapping)


@app.post("/constraints")
def update_constraints(payload: ConstraintsPayload) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			if payload.course_faculty_map is not None:
				upsert_constraint(
					cur,
					"course_faculty_map",
					json.dumps(payload.course_faculty_map),
				)
			if payload.batch_course_map is not None:
				upsert_constraint(
					cur,
					"batch_course_map",
					json.dumps(payload.batch_course_map),
				)
			if payload.rules:
				for key, value in payload.rules.items():
					upsert_constraint(cur, key, json.dumps(value))
		conn.commit()
	return {"status": "ok"}


@app.get("/constraints")
def get_constraints() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT name, value FROM constraint_rules;")
			rows = cur.fetchall()
	rules: Dict[str, Any] = {}
	for name, value in rows:
		if not value:
			continue
		try:
			rules[name] = json.loads(value)
		except json.JSONDecodeError:
			rules[name] = value
	return {
		"course_faculty_map": rules.get("course_faculty_map", {}),
		"batch_course_map": rules.get("batch_course_map", {}),
		"rules": {
			key: val
			for key, val in rules.items()
			if key not in {"course_faculty_map", "batch_course_map"}
		},
	}


@app.post("/import-csv")
def import_csv(
	entity: str = Form(...),
	file: UploadFile = File(...),
) -> Dict[str, Any]:
	target = entity.strip().lower()
	content = file.file.read()
	reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
	success = 0
	errors: List[str] = []

	with get_connection() as conn:
		with conn.cursor() as cur:
			for row_no, row in enumerate(reader, start=2):
				try:
					if target == "faculty":
						name = (row.get("name") or "").strip()
						department = (row.get("department") or "").strip()
						email = (row.get("email") or "").strip()
						if not name:
							raise ValueError("Missing name")
						cur.execute(
							"INSERT INTO faculty (name, department, email) VALUES (%s, %s, %s);",
							(name, department or None, email or None),
						)
					elif target == "course":
						name = (row.get("name") or "").strip()
						lectures = int(row.get("lectures_per_week", 1))
						is_lab = str(row.get("is_lab", "false")).lower() == "true"
						code = (row.get("code") or "").strip()
						duration = float(row.get("duration_hours", 1.0))
						if not name:
							raise ValueError("Missing name")
						cur.execute(
							"""
							INSERT INTO course (name, code, lectures_per_week, is_lab, duration_hours)
							VALUES (%s, %s, %s, %s, %s);
							""",
							(name, code or None, lectures, is_lab, duration),
						)
					elif target == "batch":
						name = (row.get("name") or "").strip()
						size = int(row.get("size", 1))
						semester = int(row.get("semester", 1))
						if not name:
							raise ValueError("Missing name")
						cur.execute(
							"INSERT INTO batch (name, size, semester) VALUES (%s, %s, %s);",
							(name, size, semester),
						)
					elif target == "room":
						name = (row.get("name") or "").strip()
						room_number = (row.get("room_number") or name).strip()
						building = (row.get("building") or "").strip()
						capacity = int(row.get("capacity", 1))
						is_lab = str(row.get("is_lab", "false")).lower() == "true"
						if not name:
							raise ValueError("Missing name")
						cur.execute(
							"""
							INSERT INTO room (name, room_number, building, capacity, is_lab)
							VALUES (%s, %s, %s, %s, %s);
							""",
							(name, room_number or None, building or None, capacity, is_lab),
						)
					elif target == "timeslot":
						day = (row.get("day") or "").strip()
						start_time = (row.get("start_time") or "").strip()
						end_time = (row.get("end_time") or "").strip()
						if not day or not start_time or not end_time:
							raise ValueError("Missing day/start_time/end_time")
						cur.execute(
							"INSERT INTO timeslot (day, start_time, end_time) VALUES (%s, %s, %s);",
							(day, start_time, end_time),
						)
					elif target == "availability":
						faculty_id = int(row.get("faculty_id", 0))
						timeslot_id = int(row.get("timeslot_id", 0))
						if faculty_id <= 0 or timeslot_id <= 0:
							raise ValueError("Missing faculty_id/timeslot_id")
						cur.execute(
							"""
							INSERT INTO faculty_availability (faculty_id, timeslot_id)
							VALUES (%s, %s) ON CONFLICT DO NOTHING;
							""",
							(faculty_id, timeslot_id),
						)
					else:
						raise ValueError(f"Unsupported entity: {target}")
					success += 1
				except Exception as exc:
					errors.append(f"Row {row_no}: {exc}")
		conn.commit()

	return {"inserted": success, "errors": errors}


@app.put("/update-data")
def update_data(payload: UpdatePayload) -> Dict[str, Any]:
	entity = payload.entity.strip().lower()
	allowed_fields = {
		"faculty": ["name", "department", "email"],
		"course": ["name", "code", "lectures_per_week", "is_lab", "duration_hours"],
		"batch": ["name", "size", "semester"],
		"room": ["name", "room_number", "building", "capacity", "is_lab"],
		"timeslot": ["day", "start_time", "end_time"],
	}
	if entity not in allowed_fields:
		raise HTTPException(status_code=400, detail="Unsupported entity")

	updates = {k: v for k, v in payload.data.items() if k in allowed_fields[entity]}
	if not updates:
		raise HTTPException(status_code=400, detail="No valid fields to update")

	set_clause = ", ".join([f"{key}=%s" for key in updates.keys()])
	values = list(updates.values()) + [payload.id]

	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				f"UPDATE {entity} SET {set_clause} WHERE id=%s;",
				values,
			)
			if cur.rowcount == 0:
				raise HTTPException(status_code=404, detail="Record not found")
		conn.commit()

	return {"updated": payload.id}


@app.post("/generate-timetable")
def generate_timetable() -> Dict[str, Any]:
	clear_schedule()
	run_engine()
	return {"status": "ok", **get_counts()}


@app.post("/regenerate")
def regenerate() -> Dict[str, Any]:
	clear_schedule()
	run_engine()
	return {"status": "ok", **get_counts()}


@app.get("/timetable/batch/{batch_id}")
def get_timetable_by_batch(batch_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT
					t.id,
					t.batch_id,
					b.name AS batch_name,
					t.course_id,
					c.name AS course_name,
					t.faculty_id,
					f.name AS faculty_name,
					t.room_id,
					r.name AS room_name,
					t.timeslot_id,
					ts.day,
					ts.start_time,
					ts.end_time
				FROM timetable t
				JOIN batch b ON t.batch_id = b.id
				JOIN course c ON t.course_id = c.id
				JOIN faculty f ON t.faculty_id = f.id
				JOIN room r ON t.room_id = r.id
				JOIN timeslot ts ON t.timeslot_id = ts.id
				WHERE t.batch_id = %s
				ORDER BY ts.day, ts.start_time;
				""",
				(batch_id,),
			)
			rows = cur.fetchall()

	entries = [
		{
			"id": r[0],
			"batch_id": r[1],
			"batch_name": r[2],
			"course_id": r[3],
			"course_name": r[4],
			"faculty_id": r[5],
			"faculty_name": r[6],
			"room_id": r[7],
			"room_name": r[8],
			"timeslot_id": r[9],
			"day": r[10],
			"start_time": r[11].strftime("%H:%M"),
			"end_time": r[12].strftime("%H:%M"),
		}
		for r in rows
	]
	return {"items": entries}


@app.get("/timetable/faculty/{faculty_id}")
def get_timetable_by_faculty(faculty_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT
					t.id,
					t.faculty_id,
					f.name AS faculty_name,
					t.course_id,
					c.name AS course_name,
					t.batch_id,
					b.name AS batch_name,
					t.room_id,
					r.name AS room_name,
					t.timeslot_id,
					ts.day,
					ts.start_time,
					ts.end_time
				FROM timetable t
				JOIN faculty f ON t.faculty_id = f.id
				JOIN course c ON t.course_id = c.id
				JOIN batch b ON t.batch_id = b.id
				JOIN room r ON t.room_id = r.id
				JOIN timeslot ts ON t.timeslot_id = ts.id
				WHERE t.faculty_id = %s
				ORDER BY ts.day, ts.start_time;
				""",
				(faculty_id,),
			)
			rows = cur.fetchall()

	entries = [
		{
			"id": r[0],
			"faculty_id": r[1],
			"faculty_name": r[2],
			"course_id": r[3],
			"course_name": r[4],
			"batch_id": r[5],
			"batch_name": r[6],
			"room_id": r[7],
			"room_name": r[8],
			"timeslot_id": r[9],
			"day": r[10],
			"start_time": r[11].strftime("%H:%M"),
			"end_time": r[12].strftime("%H:%M"),
		}
		for r in rows
	]
	return {"items": entries}


@app.get("/timetable/room/{room_id}")
def get_timetable_by_room(room_id: int) -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT
					t.id,
					t.room_id,
					r.name AS room_name,
					t.course_id,
					c.name AS course_name,
					t.batch_id,
					b.name AS batch_name,
					t.faculty_id,
					f.name AS faculty_name,
					t.timeslot_id,
					ts.day,
					ts.start_time,
					ts.end_time
				FROM timetable t
				JOIN room r ON t.room_id = r.id
				JOIN course c ON t.course_id = c.id
				JOIN batch b ON t.batch_id = b.id
				JOIN faculty f ON t.faculty_id = f.id
				JOIN timeslot ts ON t.timeslot_id = ts.id
				WHERE t.room_id = %s
				ORDER BY ts.day, ts.start_time;
				""",
				(room_id,),
			)
			rows = cur.fetchall()

	entries = [
		{
			"id": r[0],
			"room_id": r[1],
			"room_name": r[2],
			"course_id": r[3],
			"course_name": r[4],
			"batch_id": r[5],
			"batch_name": r[6],
			"faculty_id": r[7],
			"faculty_name": r[8],
			"timeslot_id": r[9],
			"day": r[10],
			"start_time": r[11].strftime("%H:%M"),
			"end_time": r[12].strftime("%H:%M"),
		}
		for r in rows
	]
	return {"items": entries}


@app.get("/conflicts")
def get_conflicts() -> Dict[str, Any]:
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				"""
				SELECT id, type, description, created_at
				FROM conflicts
				ORDER BY created_at DESC, id DESC;
				"""
			)
			rows = cur.fetchall()

	items = [
		{
			"id": r[0],
			"type": r[1],
			"description": r[2],
			"created_at": r[3].isoformat(),
		}
		for r in rows
	]
	return {"items": items}