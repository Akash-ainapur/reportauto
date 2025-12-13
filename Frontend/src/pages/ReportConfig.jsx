import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import GlassCard from "../components/GlassCard";
import Footer from "../components/Footer";
import { cn } from "../lib/utils";
import { Save, FileText, Download, Loader2 } from "lucide-react";

const ReportConfig = () => {
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
    const [progressMsg, setProgressMsg] = useState("Initializing...");
    const [message, setMessage] = useState({ text: "", type: "" });
    const [showDownload, setShowDownload] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);



    const fetchData = async () => {
        // Timeout promise to prevent infinite loading
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error("Request timed out")), 5000)
        );

        try {
            const fetchPromise = fetch('/api/data');
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
            const newState = JSON.parse(JSON.stringify(prev)); // Deep clone for safety
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

    const handleSave = async (e) => {
        e.preventDefault();
        setMessage({ text: "Saving...", type: "info" });
        try {
            const response = await fetch('/api/save', { // Assuming /api/save endpoint
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                showMessage("Configuration saved successfully!", "success");
            } else {
                showMessage("Failed to save configuration", "error");
            }
        } catch (error) {
            console.error("Save error:", error);
            showMessage("Error saving configuration", "error");
        }
    };

    const showMessage = (text, type) => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: "", type: "" }), 5000);
    };

    const handleGenerate = async () => {
        setGenerating(true);
        setShowDownload(false);
        setProgressMsg("Starting generation...");

        try {
            // 1. Start Generation
            const response = await fetch('/api/generate', { method: 'POST' });

            if (response.status === 202 || response.status === 200) {
                // 2. Start Polling
                const pollInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch('/api/status');
                        const status = await statusRes.json();

                        // Update Loading Message
                        if (status.current_step) {
                            setProgressMsg(status.current_step);
                        }

                        if (!status.running) {
                            clearInterval(pollInterval);
                            setGenerating(false);

                            if (status.error) {
                                showMessage('Error: ' + status.error, 'error');
                            } else {
                                showMessage('Report Generated Successfully!', 'success');
                                setShowDownload(true);
                            }
                        }
                    } catch (err) {
                        console.error("Polling error", err);
                    }
                }, 1500); // Poll every 1.5 seconds

            } else {
                const result = await response.json();
                setGenerating(false);
                showMessage('Error: ' + (result.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            setGenerating(false);
            showMessage('Network connection error. Check backend.', 'error');
        }
    };

    const handleDownload = () => {
        window.location.href = '/api/download';
    };

    if (loading) return <div className="text-white text-center pt-20">Loading configuration...</div>;

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-background">
            <Navbar />

            {/* Toast Message */}
            {message.text && (
                <div className={cn(
                    "fixed top-24 right-4 z-50 px-6 py-3 rounded-xl backdrop-blur-md shadow-lg transition-all",
                    message.type === 'error' ? "bg-red-500/80 text-white" : "bg-green-500/80 text-white"
                )}>
                    {message.text}
                </div>
            )}

            {/* Generating Overlay */}
            {generating && (
                <div className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center text-center p-4">
                    <Loader2 className="w-16 h-16 text-primary animate-spin mb-6" />
                    <h2 className="text-3xl font-bold text-white mb-2">Generating Report...</h2>
                    <p className="text-xl text-purple-300 font-medium animate-pulse">{progressMsg}</p>
                    <p className="text-gray-500 mt-4 text-sm">This usually takes about 30-60 seconds.</p>
                </div>
            )}

            <div className="max-w-5xl mx-auto space-y-8">
                <div className="text-center space-y-2">
                    <h1 className="text-4xl font-bold text-white">Report Configuration</h1>
                    <p className="text-gray-400">Update the Master Data Source for Automated Report Generation</p>
                </div>

                <form onSubmit={handleSave} className="space-y-8">
                    {/* Global Metadata */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Global Metadata</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                                        className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none"
                                    />
                                </div>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Styles */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Font Styles (Size)</h2>
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
                                        className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none"
                                    />
                                </div>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Students - Dynamic Array */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Students</h2>
                        <div className="space-y-6">
                            {data.people.students.map((student, index) => (
                                <div key={index} className="p-4 bg-white/5 rounded-xl border border-white/5 space-y-4">
                                    <h4 className="font-bold text-primary">Student {index + 1}</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-xs text-gray-400">USN</label>
                                            <input
                                                value={student.usn || ""}
                                                onChange={(e) => updateArrayItem("students", index, "usn", e.target.value)}
                                                className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white"
                                            />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-xs text-gray-400">Name</label>
                                            <input
                                                value={student.name || ""}
                                                onChange={(e) => updateArrayItem("students", index, "name", e.target.value)}
                                                className="w-full bg-black/20 border border-white/10 rounded px-3 py-2 text-white"
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {data.people.students.length === 0 && <p className="text-gray-500 italic">No students found in data.</p>}
                        </div>
                    </GlassCard>

                    {/* Guide - Dynamic Array */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Internal Guide</h2>
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

                    {/* Approvers */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Approvers</h2>
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
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Certificate Info</h2>
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
                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none h-24"
                                        />
                                    ) : (
                                        <input
                                            type="text"
                                            value={data.certificate_info?.[field.id] || ""}
                                            onChange={(e) => handleChange("certificate_info", field.id, e.target.value)}
                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none"
                                        />
                                    )}
                                </div>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Report Content */}
                    <GlassCard className="p-8">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Report Content</h2>
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">Abstract</label>
                                <textarea
                                    value={data.report_content?.abstract?.text || ""}
                                    onChange={(e) => handleNestedChange("report_content.abstract.text", e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none min-h-[150px]"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">Acknowledgement</label>
                                <textarea
                                    value={data.report_content?.acknowledgement?.standard_text || ""}
                                    onChange={(e) => handleNestedChange("report_content.acknowledgement.standard_text", e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none min-h-[150px]"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">Declaration</label>
                                <textarea
                                    value={data.report_content?.declaration?.text || ""}
                                    onChange={(e) => handleNestedChange("report_content.declaration.text", e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary/50 outline-none min-h-[150px]"
                                />
                            </div>
                        </div>
                    </GlassCard>

                    {/* Sticky Actions Footer */}
                    <div className="fixed bottom-0 left-0 w-full glass p-4 z-40 border-t border-white/10">
                        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-end gap-4">
                            <button
                                type="submit"
                                disabled={generating}
                                className="w-full sm:w-auto px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                            >
                                <Save className="w-5 h-5" />
                                Save Config
                            </button>
                            {!showDownload ? (
                                <button
                                    type="button"
                                    onClick={handleGenerate}
                                    disabled={generating}
                                    className="w-full sm:w-auto px-6 py-3 bg-primary hover:bg-primary/80 text-white rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(124,58,237,0.5)] flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    {generating ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
                                    {generating ? "Generating..." : "Generate Report"}
                                </button>
                            ) : (
                                <button
                                    type="button"
                                    onClick={handleDownload}
                                    className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(34,197,94,0.5)] flex items-center gap-2 animate-in fade-in slide-in-from-right"
                                >
                                    <Download className="w-5 h-5" />
                                    Download Report
                                </button>
                            )}
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
