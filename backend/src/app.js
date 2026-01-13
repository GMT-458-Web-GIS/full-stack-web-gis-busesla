const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.json({ message: "Web GIS Backend is running" });
});

module.exports = app;

const pool = require("./config/db");

app.get("/db-test", async (req, res) => {
try {
    const result = await pool.query("SELECT NOW()");
    res.json({ dbTime: result.rows[0] });
} catch (err) {
    res.status(500).json({ error: err.message });
}
});

const eventRoutes = require("./routes/events");
app.use("/api/events", eventRoutes);
