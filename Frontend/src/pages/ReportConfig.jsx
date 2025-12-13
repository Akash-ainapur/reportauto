import { useState, useEffect, useCallback } from "react";
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


    useEffect(() => {
        const fetchData = async () => {
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error("Request timed out")), 5000)
            );

            try {
                const fetchPromise = fetch(`${API_BASE}/api/data`);
                const response = await Promise.race([fetchPromise, timeoutPromise]);

                if (response.ok) {
                    const jsonData = await response.json();
                    const safeData = {
                        ...jsonData,
                        people: {
                            students: jsonData.people?.students || [],
                            guide: jsonData.people?.guide || [],
                            approvers: jsonData.people?.approvers || {}
                        }
                    };
                    setData(safeData);
                } else {
                    showMessage("Failed to load data. Is backend running?", "error");
                }
            } catch (error) {
                console.error(error);
                const errMsg = error.message === "Request timed out"
                    ? "Backend not responding (Timeout)"
                    : "Backend not connected. Run 'python app.py'";
                showMessage(errMsg, "error");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [API_BASE, showMessage]);

    const handleChange = (section, field, value) => {
        setData(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    };

    const handleNestedChange = (path, value) => {
        const keys = path.split('.');
        setData(prev => {
            const newState = JSON.parse(JSON.stringify(prev));
            let current = newState;
            for (let i = 0; i < keys.length - 1; i++) {
                if (!current[keys[i]]) current[keys[i]] = {};
                current = current[keys[i]];
            }
            current[keys[keys.length - 1]] = value;
            return newState;
        });
    };

    const updateArrayItem = (arrayName, index, field, value) => {
        setData(prev => {
            const newArray = [...(prev.people[arrayName] || [])];
            if (!newArray[index]) newArray[index] = {};
            newArray[index] = { ...newArray[index], [field]: value };
            return {
                ...prev,
                people: {
                    ...prev.people,
                    [arrayName]: newArray
                }
            };
        });
    };

    const handleDownloadProcess = async () => {
        setGenerating(true);
        // setShowDownload(false); // No longer needed as we auto-download
        setMessage({ text: "Saving configuration...", type: "info" });
        setProgress(5);

        try {
            // 1. Send Data & Start Generation (One Step)
            // We send 'data' in body, and 'sessionId' in Query param
            const response = await fetch(`${API_BASE}/api/generate?session_id=${sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.status === 409) {
                setGenerating(false);
                showMessage("Server busy! Someone else is generating. Please wait 30s.", "warning");
                return;
            }

            if (response.status === 202 || response.status === 200) {
                // 2. Poll for Status
                const pollInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch(`${API_BASE}/api/status?session_id=${sessionId}`);
                        const status = await statusRes.json();

                        // Update Loading Message
                        if (status.current_step) {
                            // setProgressMsg(status.current_step); // Not using progressMsg state currently finding by view_file
                            // wait, I don't see setProgressMsg in view_file. Let's look at view_file content.
                            // Line 24 in view_file: const [progress, setProgress] = useState(0); 
                            // Line 26: const [message, setMessage] = useState...
                            // Actually there is NO progressMsg state in the file I viewed! 
                            // Ah, GamifiedLoader might take just progress.
                            // I should update message using setMessage or showMessage if I want to show status text.
                            // Let's use showMessage for major updates or just let progress bar handle it.
                        }

                        // Update Progress
                        if (status.progress) {
                            const pct = Math.min(100, (status.progress / 14) * 100);
                            setProgress(pct);
                        }

                        if (!status.running && status.completed) {
                            clearInterval(pollInterval);
                            setGenerating(false);
                            setProgress(100);
                            showMessage('Report Ready! Downloading...', 'success');
                            triggerConfetti();

                            // 3. Trigger Download
                            window.location.href = `${API_BASE}/api/download?session_id=${sessionId}`;
                        } else if (status.error) {
                            clearInterval(pollInterval);
                            setGenerating(false);
                            showMessage('Error: ' + status.error, 'error');
                        }
                    } catch (err) {
                        console.error("Polling error", err);
                        clearInterval(pollInterval);
                        setGenerating(false);
                        showMessage("Lost connection to server.", "error");
                    }
                }, 1500);

            } else {
                const result = await response.json();
                setGenerating(false);
                showMessage('Error: ' + (result.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error("Generate error:", error);
            setGenerating(false);
            showMessage('Network connection error.', 'error');
        }
    };



    const handleSave = async (e) => {
        if (e) e.preventDefault();
        setMessage({ text: "Saving...", type: "info" });
        try {
            const response = await fetch(`${API_BASE}/api/data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                showMessage("Configuration saved successfully!", "success");
                return true;
            } else {
                showMessage("Failed to save configuration", "error");
                return false;
            }
        } catch (error) {
            console.error("Save error:", error);
            showMessage("Error saving configuration", "error");
            return false;
        }
    };


    const handleGenerate = async () => {
        // Auto-save before generating
        const saved = await handleSave();
        if (!saved) return;

        setGenerating(true);
        setShowDownload(false);
        setProgress(0);

        try {
            const response = await fetch(`${API_BASE}/api/generate`, { method: 'POST' });

            if (response.status === 409) {
                setGenerating(false);
                showMessage("Server busy! Someone else is generating. Please wait 30s.", "warning");
                return;
            }

            if (response.status === 202 || response.status === 200) {
                const pollInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch(`${API_BASE}/api/status`);
                        const status = await statusRes.json();

                        // Update Progress
                        if (status.progress) {
                            // Assuming 14 steps max
                            const pct = Math.min(100, (status.progress / 14) * 100);
                            setProgress(pct);
                        }

                        if (!status.running) {
                            clearInterval(pollInterval);
                            setGenerating(false);
                            setProgress(100);

                            if (status.error) {
                                showMessage('Error: ' + status.error, 'error');
                            } else {
                                showMessage('Report Generated Successfully!', 'success');
                                triggerConfetti();
                                setShowDownload(true);
                            }
                        }
                    } catch (err) {
                        console.error("Polling error", err);
                    }
                }, 1500);

            } else {
                const result = await response.json();
                setGenerating(false);
                showMessage('Error: ' + (result.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error("Generation error:", error);
            setGenerating(false);
            showMessage('Network connection error. Check backend.', 'error');
        }
    };

    const triggerConfetti = () => {
        const duration = 3 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        const randomInRange = (min, max) => Math.random() * (max - min) + min;

        const interval = setInterval(function () {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } });
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } });
        }, 250);
    };

    const handleDownload = () => {
        window.location.href = `${API_BASE}/api/download`;
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
                        Fill in the details below. Choose "Autopilot" for quick generation or "Director" for full control.
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

                    {/* Global Metadata - Always Visible */}
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
                                { id: "domain", label: "Domain" },
                                { id: "academic_year", label: "Academic Year" },
                                { id: "semester", label: "Semester" },
                                { id: "college_name", label: "College Name" },
                                { id: "department_name", label: "Department Name" },
                                { id: "department_abbr", label: "Dept Abbr" },
                                { id: "department_short", label: "Dept Short Name" },
                                { id: "city_code", label: "City Code" },
                                { id: "pincode", label: "Pincode" },
                                { id: "college_address", label: "College Address" },
                                { id: "project_type", label: "Project Type" },
                                { id: "course_name", label: "Course Name" },
                            ].map((field) => (
                                <div key={field.id} className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300">{field.label}</label>
                                    <input
                                        type="text"
                                        required={field.req}
                                        value={data.global_metadata?.[field.id] || ""}
                                        onChange={(e) => handleChange("global_metadata", field.id, e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-primary/50 outline-none transition-all focus:bg-black/40"
                                        placeholder={`Enter ${field.label}...`}
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
                            {data.people.students.length === 0 && <p className="text-gray-500 italic">No students found in data.</p>}
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
                        </div>
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
