const pool = require("../config/db");

exports.createEvent = async (req, res) => {
try {
    const { title, description, lat, lng } = req.body;

    const query = `
    INSERT INTO events (title, description, location)
    VALUES ($1, $2, ST_SetSRID(ST_MakePoint($3, $4), 4326))
    `;

    await pool.query(query, [title, description, lng, lat]);
    res.json({ message: "Event created successfully" });
} catch (err) {
    res.status(500).json({ error: err.message });
}
};

exports.getEvents = async (req, res) => {
try {
    const result = await pool.query(`
    SELECT id, title, description,
            ST_AsGeoJSON(location)::json AS geometry
    FROM events
    `);
    res.json(result.rows);
} catch (err) {
    res.status(500).json({ error: err.message });
}
};
