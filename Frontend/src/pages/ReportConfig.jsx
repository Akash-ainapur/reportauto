import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/clerk-react";
import Navbar from "../components/Navbar";
import GlassCard from "../components/GlassCard";
import Footer from "../components/Footer";
import GamifiedLoader from "../components/GamifiedLoader"; // Integrated Loader
import { cn } from "../lib/utils";
import { Save, FileText, Download, Loader2, Sparkles, Bot, Clapperboard } from "lucide-react";
import confetti from "canvas-confetti"; // Confetti!

const ReportConfig = () => {
    // Use Environment Variable for API Base URL - Fallback to empty string for local proxy
    const API_BASE = import.meta.env.VITE_API_URL || "";
    // Generate unique session ID on mount
    const [sessionId] = useState(() => crypto.randomUUID());
    const { getToken, userId } = useAuth();

    const [data, setData] = useState({
        global_metadata: {},
        styles: {},
        submission_info: {},
        people: { students: [], guide: [], approvers: {} },
        certificate_info: {},
        report_content: { abstract: {}, acknowledgement: {}, declaration: {} }
    });
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [progress, setProgress] = useState(0); // 0-100
    const [aiMode, setAiMode] = useState("autopilot"); // 'autopilot' | 'director'
    const [message, setMessage] = useState({ text: "", type: "" });
    const [showDownload, setShowDownload] = useState(false);

    const showMessage = useCallback((text, type) => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: "", type: "" }), 5000);
    }, []);


    const [context, setContext] = useState({ departments: [], years: [] });
    const [selectedContext, setSelectedContext] = useState({ dept: "", year: "" });

    useEffect(() => {
        // Fetch Context Data (Depts, Years)
        const fetchContext = async () => {
            try {
                const token = await getToken();
                const res = await fetch(`${API_BASE}/api/context-data`, {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (res.ok) {
                    const cData = await res.json();
                    setContext(cData);
                    // Set defaults if available - optional
                }
            } catch (e) { console.error("Context load failed", e); }
            setLoading(false); // Stop loading regardless
        };
        fetchContext();
    }, [API_BASE]);

    const handleContextChange = async (type, value) => {
        const newContext = { ...selectedContext, [type]: value };
        setSelectedContext(newContext);

        if (newContext.dept && newContext.year) {
            // Fetch Defaults
            try {
                const token = await getToken();
                const res = await fetch(`${API_BASE}/api/defaults?dept=${newContext.dept}&year=${newContext.year}`, {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (res.ok) {
                    const defaults = await res.json();

                    // Merge smartly: Don't overwrite user fields if they typed something? 
                    // Actually prompt implies "starts blank" then "populates". 
                    // If user switches dept, they probably WANT to reset fixed fields.

                    setData(prev => {
                        const isTest = newContext.dept === "TEST DEPARTMENT";
                        return {
                            ...defaults,
                            global_metadata: {
                                ...defaults.global_metadata,
                                project_title: isTest ? (defaults.global_metadata.project_title || "") : (prev.global_metadata.project_title || ""),
                                project_subtitle: isTest ? (defaults.global_metadata.project_subtitle || "") : (prev.global_metadata.project_subtitle || ""),
                                domain: isTest ? (defaults.global_metadata.domain || "") : (prev.global_metadata.domain || ""),
                                project_type: isTest ? (defaults.global_metadata.project_type || "") : (prev.global_metadata.project_type || ""),
                                course_name: isTest ? (defaults.global_metadata.course_name || "") : (prev.global_metadata.course_name || "")
                            },
                            people: {
                                ...defaults.people,
                                students: (isTest || prev.people.students.length === 0) ? defaults.people.students : prev.people.students,
                                guide: (isTest || prev.people.guide.length === 0) ? defaults.people.guide : prev.people.guide
                            },
                            ai_context: isTest ? (defaults.ai_context || "") : (prev.ai_context || "")
                        };
                    });
                }
            } catch (e) { showMessage("Failed to load defaults", "error"); }
        }
    };

    // Helper to determine if a field is "Fixed" (Institution related)
    const isFixedField = (id) => {
        const fixed = ["college_name", "department_name", "department_abbr", "department_short", "city_code", "pincode", "college_address", "academic_year", "semester"];
        return fixed.includes(id);
    };

    // Field ReadOnly Logic: Fixed fields are ReadOnly in Autopilot.
    const isReadOnly = (id) => {
        if (aiMode === "director") return false;
        return isFixedField(id);
    };

    // Styles for ReadOnly inputs
    const inputClasses = (id) => cn(
        "w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary/50 outline-none transition-all focus:bg-black/40",
        isReadOnly(id) && "opacity-60 cursor-not-allowed bg-black/40 border-transparent"
    );


    const handleChange = (section, field, value) => {
        setData(prev => ({
            ...prev,
            [section]: field ? { ...prev[section], [field]: value } : value
        }));
    };

    const handleNestedChange = (path, value) => {
        const keys = path.split('.');
        setData(prev => {
            const newData = { ...prev };
            let current = newData;
            for (let i = 0; i < keys.length - 1; i++) {
                if (!current[keys[i]]) current[keys[i]] = {};
                current = current[keys[i]];
            }
            current[keys[keys.length - 1]] = value;
            return newData;
        });
    };

    const updateArrayItem = (arrayName, index, field, value) => {
        setData(prev => ({
            ...prev,
            people: {
                ...prev.people,
                [arrayName]: prev.people[arrayName].map((item, i) =>
                    i === index ? { ...item, [field]: value } : item
                )
            }
        }));
    };

    const handleDownloadProcess = async () => {
        setGenerating(true);
        setProgress(0);
        try {
            const token = await getToken();
            const authHeaders = {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            };

            // 1. Start Generation
            const startRes = await fetch(`${API_BASE}/api/generate`, {
                method: "POST",
                headers: authHeaders,
                body: JSON.stringify({ ...data, session_id: sessionId })
            });

            if (!startRes.ok) {
                if (startRes.status === 402) throw new Error("Free limit reached! Upgrade plan.");
                else throw new Error("Failed to start generation");
            }

            const { session_id } = await startRes.json();

            // 2. Poll for Completion
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(`${API_BASE}/api/status?session_id=${session_id}`);
                    if (!statusRes.ok) return;

                    const statusData = await statusRes.json();

                    // Update Progress (0-100%)
                    // Assume 14 steps total
                    const pct = Math.min(Math.round((statusData.progress / 14) * 100), 99);
                    setProgress(pct);

                    if (statusData.error) {
                        clearInterval(pollInterval);
                        setGenerating(false);
                        showMessage(`Error: ${statusData.error}`, "error");
                    }

                    if (statusData.completed) {
                        clearInterval(pollInterval);
                        setProgress(100);

                        // 3. Download File
                        const downloadRes = await fetch(`${API_BASE}/api/download?session_id=${session_id}`, {
                            headers: { "Authorization": `Bearer ${token}` }
                        });

                        if (downloadRes.ok) {
                            const blob = await downloadRes.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = `Report_${data.global_metadata?.project_title || "Project"}.docx`;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            confetti();
                            showMessage("Report downloaded successfully!", "success");
                        } else {
                            showMessage("Download failed after generation.", "error");
                        }
                        setGenerating(false);
                    }
                } catch (e) {
                    console.error("Polling error", e);
                    // Don't stop immediately on one polling error, might be transient
                }
            }, 1000); // Poll every 1s

        } catch (e) {
            console.error(e);
            setGenerating(false);
            showMessage(e.message || "Network error", "error");
        }
    };


    if (loading) return <div className="text-white text-center pt-20">Loading configuration...</div>;

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
            <Navbar />

            {/* Toast Message */}
            {message.text && (
                <div className={cn(
                    "fixed top-24 right-4 z-50 px-6 py-4 rounded-xl backdrop-blur-md shadow-lg transition-all border border-white/10",
                    message.type === 'error' ? "bg-red-500/90 text-white" :
                        message.type === 'warning' ? "bg-yellow-500/90 text-white" :
                            "bg-green-500/90 text-white"
                )}>
                    {message.text}
                </div>
            )}

            {/* Generating Overlay */}
            {generating && (
                <div className="fixed inset-0 z-[60] bg-black/90 backdrop-blur-md flex flex-col items-center justify-center p-4">
                    <GamifiedLoader progress={progress} />
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-8 text-gray-500 hover:text-white text-sm underline"
                    >
                        Cancel / Stuck?
                    </button>
                </div>
            )}

            <div className="max-w-5xl mx-auto space-y-8">
                <div className="text-center space-y-4">
                    <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
                        Design Your Report
                    </h1>
                    <p className="text-gray-400 max-w-xl mx-auto">
                        Select your Department & Year to auto-fill college details. Then simply add your project title and the AI context.
                    </p>

                    {/* AI Mode Toggle */}
                    <div className="flex justify-center mt-6">
                        <div className="bg-white/5 p-1 rounded-full border border-white/10 flex relative">
                            <button
                                onClick={() => setAiMode("autopilot")}
                                className={cn(
                                    "px-6 py-2 rounded-full flex items-center gap-2 transition-all duration-300 relative z-10",
                                    aiMode === "autopilot" ? "text-white" : "text-gray-400 hover:text-white"
                                )}
                            >
                                <Sparkles className="w-4 h-4" />
                                <span className="font-medium">Autopilot</span>
                            </button>
                            <button
                                onClick={() => setAiMode("director")}
                                className={cn(
                                    "px-6 py-2 rounded-full flex items-center gap-2 transition-all duration-300 relative z-10",
                                    aiMode === "director" ? "text-white" : "text-gray-400 hover:text-white"
                                )}
                            >
                                <Clapperboard className="w-4 h-4" />
                                <span className="font-medium">Director Mode</span>
                            </button>

                            {/* Sliding Background */}
                            <div
                                className={cn(
                                    "absolute top-1 bottom-1 w-[50%] bg-primary/20 border border-primary/50 rounded-full transition-all duration-300 ease-in-out",
                                    aiMode === "director" ? "left-[50%]" : "left-0"
                                )}
                            />
                        </div>
                    </div>
                </div>

                <form className="space-y-8 animate-in fade-in slide-in-from-bottom duration-700" onSubmit={(e) => { e.preventDefault(); handleDownloadProcess(); }}>

                    {/* CONTEXT SELECTOR */}
                    <GlassCard className="p-8 border-primary/30">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            Start Here
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">Department</label>
                                <select
                                    value={selectedContext.dept}
                                    onChange={(e) => handleContextChange("dept", e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary/50 outline-none cursor-pointer"
                                >
                                    <option value="" disabled>Select Department</option>
                                    {context.departments.map(d => <option key={d} value={d} className="bg-gray-900">{d}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">Academic Year</label>
                                <select
                                    value={selectedContext.year}
                                    onChange={(e) => handleContextChange("year", e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary/50 outline-none cursor-pointer"
                                >
                                    <option value="" disabled>Select Year</option>
                                    {context.years.map(y => <option key={y} value={y} className="bg-gray-900">{y}</option>)}
                                </select>
                            </div>
                        </div>
                    </GlassCard>

                    {/* Global Metadata */}
                    <GlassCard className="p-8 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Bot className="w-24 h-24 text-primary" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2 flex items-center gap-2">
                            <Bot className="w-6 h-6 text-primary" />
                            Core Details
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                            {[
                                { id: "project_title", label: "Project Title", req: true },
                                { id: "project_subtitle", label: "Project Subtitle" },
                                // User defined
                                { id: "domain", label: "Domain" },
                                { id: "project_type", label: "Project Type" },
                                { id: "course_name", label: "Course Name" },
                                // Fixed / Auto-Filled
                                { id: "academic_year", label: "Academic Year" },
                                { id: "semester", label: "Semester" },
                                { id: "college_name", label: "College Name" },
                                { id: "department_name", label: "Department Name" },
                                { id: "department_abbr", label: "Dept Abbr" },
                                { id: "department_short", label: "Dept Short Name" },
                                { id: "city_code", label: "City Code" },
                                { id: "pincode", label: "Pincode" },
                                { id: "college_address", label: "College Address" },
                            ].map((field) => (
                                <div key={field.id} className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300 flex justify-between">
                                        {field.label}
                                        {isFixedField(field.id) && aiMode === "autopilot" && <span className="text-xs text-primary/70">(Auto-Filled)</span>}
                                    </label>
                                    <input
                                        type="text"
                                        required={field.req}
                                        value={data.global_metadata?.[field.id] || ""}
                                        onChange={(e) => handleChange("global_metadata", field.id, e.target.value)}
                                        readOnly={isReadOnly(field.id)}
                                        className={inputClasses(field.id)}
                                        placeholder={isReadOnly(field.id) ? "Autofilled..." : `Enter ${field.label}...`}
                                    />
                                </div>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Students - Always Visible */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Team Members</h2>
                        <div className="space-y-6">
                            {data.people.students.map((student, index) => (
                                <div key={index} className="p-4 bg-white/5 rounded-xl border border-white/5 space-y-4 hover:border-primary/30 transition-colors">
                                    <h4 className="font-bold text-primary flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs">
                                            {index + 1}
                                        </div>
                                        Student {index + 1}
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-xs text-gray-400">USN</label>
                                            <input
                                                value={student.usn || ""}
                                                onChange={(e) => updateArrayItem("students", index, "usn", e.target.value)}
                                                className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:ring-1 focus:ring-primary/50"
                                            />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-xs text-gray-400">Name</label>
                                            <input
                                                value={student.name || ""}
                                                onChange={(e) => updateArrayItem("students", index, "name", e.target.value)}
                                                className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white focus:ring-1 focus:ring-primary/50"
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {data.people.students.length === 0 && (
                                <div className="text-center py-8">
                                    <p className="text-gray-500 italic mb-4">No students added yet.</p>
                                    <button
                                        type="button"
                                        onClick={() => setData(prev => ({ ...prev, people: { ...prev.people, students: [...prev.people.students, { name: "", usn: "" }, { name: "", usn: "" }, { name: "", usn: "" }, { name: "", usn: "" }] } }))}
                                        className="text-primary hover:text-primary/80 underline"
                                    >
                                        Add 4 Students (Standard Team)
                                    </button>
                                </div>
                            )}
                        </div>
                    </GlassCard>

                    {/* Guide - Always Visible */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Guide Details</h2>
                        <div className="space-y-6">
                            {data.people.guide.map((guide, index) => (
                                <div key={index} className="p-4 bg-white/5 rounded-xl border border-white/5 space-y-4">
                                    <h4 className="font-bold text-primary">Guide {index + 1}</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {["name", "designation", "department", "role"].map(field => (
                                            <div key={field} className="space-y-1">
                                                <label className="text-xs text-gray-400 capitalize">{field}</label>
                                                <input
                                                    value={guide[field] || ""}
                                                    onChange={(e) => updateArrayItem("guide", index, field, e.target.value)}
                                                    className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                            {data.people.guide.length === 0 && (
                                <div className="text-center py-4">
                                    <button
                                        type="button"
                                        onClick={() => setData(prev => ({ ...prev, people: { ...prev.people, guide: [...prev.people.guide, { name: "", designation: "", department: "", role: "Internal Guide" }] } }))}
                                        className="text-primary hover:text-primary/80 underline"
                                    >
                                        Add Guide
                                    </button>
                                </div>
                            )}
                        </div>
                    </GlassCard>

                    {/* AI Project Context - NEW */}
                    <GlassCard className="p-8 border-green-500/30 relative overflow-hidden">
                        <div className="absolute -right-10 -top-10 w-40 h-40 bg-green-500/10 rounded-full blur-3xl"></div>
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                            <Sparkles className="w-6 h-6 text-green-400" />
                            AI Project Context
                        </h2>
                        <p className="text-gray-400 text-sm mb-4">
                            Paste your project abstract, problem statement, rough notes, or even code snippets here.
                            The AI will use this single source to generate the entire report content (Abstract, Introduction, etc.).
                        </p>
                        <textarea
                            value={data.ai_context || ""}
                            onChange={(e) => handleChange("ai_context", null, e.target.value)}
                            // handleChange usually takes (section, field, value). 
                            // But ai_context is root level in my plan? 
                            // Wait, handleChange implementation: setData(prev => ({...prev, [section]: { ...prev[section], [field]: value } }));
                            // This expects nested.
                            // I should fix handleChange or use a direct setter.
                            // Let's use a direct setter for root level or adjust handleChange.
                            // Let's modify: onChange={(e) => setData(prev => ({ ...prev, ai_context: e.target.value }))}
                            className="w-full bg-black/20 border border-green-500/20 rounded-xl px-6 py-4 text-white focus:ring-2 focus:ring-green-500/50 outline-none min-h-[200px] font-mono text-sm leading-relaxed"
                            placeholder="Example: My project is about a Smart Irrigation System using IoT. It uses Arduino, Moisture Sensors, and a Python backend. It solves the problem of water wastage in agriculture..."
                        />
                    </GlassCard>


                    {/* DIRECTOR MODE SECTIONS */}
                    {aiMode === "director" && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-left duration-500">

                            <div className="flex items-center gap-4 my-8">
                                <div className="h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent flex-1" />
                                <span className="text-purple-300 font-bold tracking-wider text-sm uppercase">Director Mode Active</span>
                                <div className="h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent flex-1" />
                            </div>

                            {/* Styles */}
                            <GlassCard className="p-8 border-purple-500/20">
                                <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Font Styling</h2>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    {[
                                        { id: "project_title", label: "Project Title Size" },
                                        { id: "project_subtitle", label: "Project Subtitle Size" },
                                        { id: "student_details", label: "Student Details Size" },
                                        { id: "guide_name", label: "Guide Name Size" },
                                        { id: "guide_label", label: "Guide Label Size" },
                                        { id: "header_footer", label: "Header/Footer Size" },
                                    ].map((field) => (
                                        <div key={field.id} className="space-y-2">
                                            <label className="text-sm font-medium text-gray-300">{field.label}</label>
                                            <input
                                                type="number"
                                                value={data.styles?.[field.id] || ""}
                                                onChange={(e) => handleChange("styles", field.id, parseInt(e.target.value))}
                                                className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none"
                                            />
                                        </div>
                                    ))}
                                </div>
                            </GlassCard>

                            {/* Approvers */}
                            <GlassCard className="p-8 border-purple-500/20">
                                <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Approvals</h2>
                                <div className="space-y-6">
                                    <div className="space-y-4">
                                        <h4 className="font-bold text-purple-300">HOD</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            {['name', 'designation', 'department'].map(field => (
                                                <div key={field} className="space-y-1">
                                                    <label className="text-xs text-gray-400 capitalize">{field}</label>
                                                    <input
                                                        value={data.people?.approvers?.hod?.[field] || ""}
                                                        onChange={(e) => handleNestedChange(`people.approvers.hod.${field}`, e.target.value)}
                                                        className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white"
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="space-y-4 pt-4 border-t border-white/5">
                                        <h4 className="font-bold text-purple-300">Principal</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {['name', 'designation'].map(field => (
                                                <div key={field} className="space-y-1">
                                                    <label className="text-xs text-gray-400 capitalize">{field}</label>
                                                    <input
                                                        value={data.people?.approvers?.principal?.[field] || ""}
                                                        onChange={(e) => handleNestedChange(`people.approvers.principal.${field}`, e.target.value)}
                                                        className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white"
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </GlassCard>

                            {/* Certificate Info */}
                            <GlassCard className="p-8 border-purple-500/20">
                                <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Certificate Details</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {[
                                        { id: "project_type", label: "Project Type" },
                                        { id: "certificate_title", label: "Certificate Title" },
                                        { id: "guide_name", label: "Guide Name (Cert)" },
                                        { id: "guide_designation", label: "Guide Designation (Cert)", type: 'textarea' },
                                        { id: "hod_name", label: "HOD Name (Cert)" },
                                        { id: "hod_designation", label: "HOD Designation (Cert)", type: 'textarea' },
                                        { id: "dean_name", label: "Dean Name (Cert)" },
                                        { id: "dean_designation", label: "Dean Designation (Cert)", type: 'textarea' },
                                    ].map((field) => (
                                        <div key={field.id} className="space-y-2">
                                            <label className="text-sm font-medium text-gray-300">{field.label}</label>
                                            {field.type === 'textarea' ? (
                                                <textarea
                                                    value={data.certificate_info?.[field.id] || ""}
                                                    onChange={(e) => handleChange("certificate_info", field.id, e.target.value)}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none h-24"
                                                />
                                            ) : (
                                                <input
                                                    type="text"
                                                    value={data.certificate_info?.[field.id] || ""}
                                                    onChange={(e) => handleChange("certificate_info", field.id, e.target.value)}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none"
                                                />
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </GlassCard>

                            {/* Report Content */}
                            <GlassCard className="p-8 border-purple-500/20">
                                <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Custom Text Content</h2>
                                <div className="space-y-6">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-300">Abstract</label>
                                        <textarea
                                            value={data.report_content?.abstract?.text || ""}
                                            onChange={(e) => handleNestedChange("report_content.abstract.text", e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none min-h-[150px]"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-300">Acknowledgement</label>
                                        <textarea
                                            value={data.report_content?.acknowledgement?.standard_text || ""}
                                            onChange={(e) => handleNestedChange("report_content.acknowledgement.standard_text", e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none min-h-[150px]"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-gray-300">Declaration</label>
                                        <textarea
                                            value={data.report_content?.declaration?.text || ""}
                                            onChange={(e) => handleNestedChange("report_content.declaration.text", e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500/50 outline-none min-h-[150px]"
                                        />
                                    </div>
                                </div>
                            </GlassCard>
                        </div>
                    )}

                    {/* Sticky Actions Footer */}
                    <div className="fixed bottom-0 left-0 w-full glass p-4 z-40 border-t border-white/10">
                        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-end">
                            <button
                                type="submit"
                                disabled={generating}
                                className={cn(
                                    "w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-primary to-purple-600 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-3 text-lg disabled:opacity-50",
                                    generating
                                        ? "cursor-not-allowed grayscale"
                                        : "hover:shadow-[0_0_40px_rgba(124,58,237,0.6)] hover:scale-105"
                                )}
                            >
                                {generating ? <Loader2 className="w-6 h-6 animate-spin" /> : <Download className="w-6 h-6" />}
                                {generating ? "Generating Report..." : "Download Report"}
                            </button>
                        </div>
                    </div>
                    <div className="h-20" /> {/* Spacer for footer */}
                </form>
            </div>
            <Footer />
        </div>
    );
};

export default ReportConfig;
