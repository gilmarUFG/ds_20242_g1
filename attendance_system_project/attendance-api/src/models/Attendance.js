const mongoose = require("mongoose");
const { Schema } = mongoose;

const AttendanceSchema = new Schema({
  student_id: {
    type: String,
    required: [true, "Student ID is required"], // Campo obrigatório
    trim: true, // Remove espaços em branco desnecessários
  },
  captureTimestamp: {
    type: Date,
    required: [true, "Capture timestamp is required"], // Campo obrigatório
    default: Date.now, // Define um valor padrão de timestamp
  },
  confidence_score: {
    type: Number,
    required: [true, "Confidence score is required"], // Campo obrigatório
    min: [0, "Confidence score must be at least 0"], // Valor mínimo 0
    max: [1, "Confidence score must be at most 1"], // Valor máximo 1
  },
  attendance_status: {
    type: String,
    enum: ["present", "absent", "discipline_not_found", "already_present"], // Valores permitidos
    default: "present",
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model("Attendance", AttendanceSchema);
