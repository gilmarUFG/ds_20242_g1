const express = require("express");
const Attendance = require("../models/Attendance");
const router = express.Router();

router.post("/mark", async (req, res) => {
  const { student_id, classId, date } = req.body;

  try {
    const attendance = new Attendance({ student_id, classId, date });
    await attendance.save();

    res.status(201).json({ message: "Attendance marked successfully" });
  } catch (error) {
    res.status(500).json({ error: "Error marking attendance" });
  }
});

module.exports = router;
