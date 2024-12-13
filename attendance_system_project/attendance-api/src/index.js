require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8001;

app.post("/api/register_attendance", async (req, res) => {
  try {
    const { student_id, timestamp, confidence } = req.body;

    if (confidence < 0.95) {
      return res.status(400).json({
        message:
          "Confiança insuficiente. O valor de 'confidence' deve ser maior ou igual a 0.95.",
      });
    }

    // Simula um erro aleatório para o status de presença
    const systemErrorChance = Math.random(); // Gera um número aleatório entre 0 e 1

    if (systemErrorChance > 0.8) {
      // 20% chance de erro crítico
      throw new Error("Simulação de erro crítico no sistema.");
    }

    // Simula um erro aleatório para o status de presença
    const errorChance = Math.random(); // Gera um número aleatório entre 0 e 1
    let attendanceStatus;

    if (errorChance > 0.66) {
      // 20% chance de erro
      const statuses = ["absent", "discipline_not_found", "already_present"];
      attendanceStatus = statuses[Math.floor(Math.random() * statuses.length)]; // Escolhe um status aleatório de erro
    } else {
      attendanceStatus = "present"; // Status padrão
    }

    // Retorna o campo solicitado no response
    res.status(200).json({
      student_id: student_id,
      timestamp: timestamp,
      confidence: confidence,
      attendance_status: attendanceStatus,
    });
  } catch (error) {
    console.error("Erro ao cadastrar presença:", error);
    res.status(500).json({ message: "Erro ao cadastrar presença.", error });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
