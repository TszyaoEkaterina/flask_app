import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./FitnessClassManagement.css";

const FitnessClassManagement = () => {
    const [classes, setClasses] = useState([]);
    const [trainers, setTrainers] = useState([]);
    const [rooms, setRooms] = useState([]);
    const [filters, setFilters] = useState({ dateFrom: "", dateTo: "", trainer: "", room: "" });
    const [statistics, setStatistics] = useState(null);
    const [editingClass, setEditingClass] = useState(null);
    const [editFormData, setEditFormData] = useState({
        description: "",
        date: "",
        time: "",
        duration: "",
        trainer_id: "",
        room_id: "",
        restrictions: "",
    });
    const navigate = useNavigate();

    useEffect(() => {
        fetchTrainers();
        fetchRooms();
    }, []);

    const fetchTrainers = async () => {
        const response = await fetch("http://localhost:5000/api/trainers");
        const data = await response.json();
        setTrainers(data);
    };
    
    const fetchRooms = async () => {
        const response = await fetch("http://localhost:5000/api/rooms");
        const data = await response.json();
        setRooms(data);
    };

    const fetchClasses = async () => {
        const queryParams = new URLSearchParams({
            dateFrom: filters.dateFrom || "",
            dateTo: filters.dateTo || "",
            trainer: filters.trainer || "",
            room: filters.room || ""
        }).toString();
    
        const classResponse = await fetch(`http://localhost:5000/api/classes?${queryParams}`);
        const classData = await classResponse.json();
        setClasses(classData.classes);
        const statResponse = await fetch(`http://localhost:5000/api/stats?${queryParams}`);
        const statData = await statResponse.json();
        setStatistics(statData);
    };
    const handleDelete = async (classId) => {
        if (!window.confirm("Are you sure you want to delete this class?")) {
            console.log("class id:", classId);
            return;
        }
    
        try {
            const response = await fetch(`http://localhost:5000/api/classes/${classId}`, {
                method: "DELETE",
            });
    
            const data = await response.json();
            if (data.success) {
                alert("Class deleted successfully!");
                fetchClasses();
            } else {
                alert("Error: " + data.error);
            }
        } catch (error) {
            console.error("Failed to delete class:", error);
            alert("An error occurred while deleting the class.");
        }
    };

    // Block for editing/updating data
    const handleEditClick = (fitClass) => {
        setEditingClass(fitClass.class_id);
        setEditFormData({
            description: fitClass.description,
            date: fitClass.date,
            time: fitClass.time,
            duration: fitClass.duration,
            trainer_id: fitClass.trainer_id,
            room_id: fitClass.room_id,
            restrictions: fitClass.restrictions || "",
        });
    };
    
    const handleInputChange = (e) => {
        setEditFormData({ ...editFormData, [e.target.name]: e.target.value });
    };
    
    const handleUpdateClass = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/classes/${editingClass}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(editFormData),
            });
    
            if (response.ok) {
                alert("Class updated successfully!");
                setEditingClass(null);
                fetchClasses(); // Reload
            } else {
                const errorData = await response.json();
                alert(`Error updating class: ${errorData.error}`);
            }
        } catch (error) {
            console.error("Update error:", error);
            alert("Failed to update class.");
        }
    };

    return (
        <div className="content">
            <h1 className="heading-title">Fitness Class Management</h1>
            <button onClick={() => navigate("/add")} className="btn add-btn">Add New Class</button>
            
            <div className="filters">
                <input type="date" value={filters.dateFrom} onChange={e => setFilters({...filters, dateFrom: e.target.value})} className="date fron-date" placeholder="From Date" />
                <input type="date" value={filters.dateTo} onChange={e => setFilters({...filters, dateTo: e.target.value})} className="date to-date" placeholder="To Date" />
                <select value={filters.trainer} onChange={e => setFilters({...filters, trainer: e.target.value})} className="trainers">
                    <option value="">All Trainers</option>
                    {trainers.map(trainer => (
                    <option key={trainer.id} value={trainer.id}>{trainer.name}</option>
                    ))}
                </select>
                <select value={filters.room} onChange={e => setFilters({...filters, room: e.target.value})} className="rooms">
                    <option value="">All Rooms</option>
                    {rooms.map(room => (
                    <option key={room.id} value={room.id}>{room.name}</option>
                    ))}
                </select>
                <button onClick={fetchClasses} className="filter-btn">
                    Search & Generate Report
                </button>
            </div>
            
            <div className="results">
                {classes.map(fitClass => (
                    <div key={fitClass.class_id} className="item result-class-card">
                        <div>
                            <p className="class-descr">{fitClass.description}</p>
                            <p>Id: {fitClass.class_id} | {fitClass.date} | {fitClass.time} | {fitClass.duration} mins</p>
                            <p>Trainer id: {fitClass.trainer_id} | Room id: {fitClass.room_id}</p>
                            <p>Restrictions: {fitClass.restrictions || "N/A"}</p>
                        </div>
                        <div>
                            <button onClick={() => handleEditClick(fitClass)} className="btn edit-btn">Edit</button>
                            <button onClick={() => handleDelete(fitClass.class_id)} className="btn delete-btn">Delete</button>
                        </div>
                    </div>
                ))}
            </div>
            
            {statistics && (
                <div className="statistics-container">
                <h2>Class Statistics</h2>
                    <p><strong>Average Duration:</strong> {statistics.average_duration.toFixed(2)} minutes</p>
                    <p><strong>Average Participants:</strong> {statistics.average_participants.toFixed(2)}</p>
                    <p><strong>Average VIP Members:</strong> {statistics.average_vips.toFixed(2)}</p>
                </div>
            )}

            {editingClass && (
                <div className="edit-modal">
                    <h3>Edit Class</h3>
                    <input type="text" name="description" value={editFormData.description} onChange={handleInputChange} placeholder="Description" />
                    <input type="date" name="date" value={editFormData.date} onChange={handleInputChange} />
                    <input type="time" name="time" value={editFormData.time} onChange={handleInputChange} />
                    <input type="number" name="duration" value={editFormData.duration} onChange={handleInputChange} placeholder="Duration (mins)" />
                    <input type="number" name="trainer_id" value={editFormData.trainer_id} onChange={handleInputChange} placeholder="Trainer ID" />
                    <input type="number" name="room_id" value={editFormData.room_id} onChange={handleInputChange} placeholder="Room ID" />
                    <input type="text" name="restrictions" value={editFormData.restrictions} onChange={handleInputChange} placeholder="Restrictions" />
                    <button onClick={handleUpdateClass} className="btn save-btn">Save</button>
                    <button onClick={() => setEditingClass(null)} className="btn cancel-btn">Cancel</button>
                </div>
            )}
        </div>
    );
};

export default FitnessClassManagement;
