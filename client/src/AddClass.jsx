import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AddClass.css";

const AddClass = () => {
    const [formData, setFormData] = useState({
        description: "",
        date: "",
        time: "",
        duration: "",
        trainer_id: "",
        room_id: "",
        restrictions: ""
    });

    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch("http://localhost:5000/api/classes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });
        console.log("Response Status:", response.status);
        const responseData = await response.json();
        console.log("Response Data:", responseData);
        if (response.ok) {
            alert("Class added successfully!");
            navigate("/");  // Redirect back to the main page
        } else {
            alert("Failed to add class:", response);
        }
    };

    return (
        <div className="add-class-container">
            <div className="form-card">
                <h2 className="title">Add a New Fitness Class</h2>
                <form onSubmit={handleSubmit} className="add-class-form">
                    <div className="input-group input-descr">
                        <label>Description:</label>
                        <input type="text" name="description" value={formData.description} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-date">
                        <label>Date:</label>
                        <input type="date" name="date" value={formData.date} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-time">
                        <label>Time:</label>
                        <input type="time" name="time" value={formData.time} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-duration">
                        <label>Duration (minutes):</label>
                        <input type="number" name="duration" value={formData.duration} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-trainer_id">
                        <label>Trainer id:</label>
                        <input type="number" name="trainer_id" value={formData.trainer_id} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-room_id">
                        <label>Room:</label>
                        <input type="number" name="room_id" value={formData.room_id} onChange={handleChange} required />
                    </div>

                    <div className="input-group input-restrictions">
                        <label>Restrictions:</label>
                        <input type="text" name="restrictions" value={formData.restrictions} onChange={handleChange} />
                    </div>

                    <button type="submit" className="submit-btn">Add Class</button>
                </form>
            </div>
        </div>
    );
};

export default AddClass;
