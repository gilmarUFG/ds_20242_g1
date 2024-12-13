require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8001;

// Helper function to format the log timestamp
const getFormattedTimestamp = () => {
  return new Date().toISOString();
};

// Helper function to format the log message
const formatLogMessage = (type, data) => {
  return `[${getFormattedTimestamp()}] ${type}:\n${JSON.stringify(
    data,
    null,
    2
  )}`;
};

app.post("/api/register_attendance", async (req, res) => {
  // Log the incoming request
  console.log("\n" + "=".repeat(50));
  console.log(
    formatLogMessage("REQUEST", {
      method: "POST",
      path: "/api/register_attendance",
      body: req.body,
      headers: req.headers,
    })
  );

  try {
    const { student_id, timestamp, confidence } = req.body;

    if (confidence < 0.95) {
      const errorResponse = {
        message:
          "Confiança insuficiente. O valor de 'confidence' deve ser maior ou igual a 0.95.",
      };
      console.log(formatLogMessage("RESPONSE ERROR", errorResponse));
      return res.status(400).json(errorResponse);
    }

    const systemErrorChance = Math.random();

    if (systemErrorChance > 0.8) {
      throw new Error("Simulação de erro crítico no sistema.");
    }

    const errorChance = Math.random();
    let attendanceStatus;

    if (errorChance > 0.66) {
      const statuses = ["absent", "discipline_not_found", "already_present"];
      attendanceStatus = statuses[Math.floor(Math.random() * statuses.length)];
    } else {
      attendanceStatus = "present";
    }

    const response = {
      student_id: student_id,
      timestamp: timestamp,
      confidence: confidence,
      attendance_status: attendanceStatus,
    };

    // Log the successful response
    console.log(formatLogMessage("RESPONSE SUCCESS", response));
    console.log("=".repeat(50) + "\n");

    res.status(200).json(response);
  } catch (error) {
    const errorResponse = {
      message: "Erro ao cadastrar presença.",
      error: error.message,
    };

    // Log the error response
    console.log(formatLogMessage("RESPONSE ERROR", errorResponse));
    console.log("=".repeat(50) + "\n");

    console.error("Erro ao cadastrar presença:", error);
    res.status(500).json(errorResponse);
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
