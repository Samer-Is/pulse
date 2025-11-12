"use client";

import { useState } from "react";
import { FileText, Download, Plus, Trash2, Loader2 } from "lucide-react";

interface PersonalInfo {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  website: string;
  linkedin: string;
  github: string;
}

interface Experience {
  job_title: string;
  company: string;
  location: string;
  start_date: string;
  end_date: string;
  description: string;
  responsibilities: string[];
}

interface Education {
  degree: string;
  institution: string;
  location: string;
  start_date: string;
  end_date: string;
  gpa: string;
  achievements: string[];
}

interface Skill {
  category: string;
  skills: string[];
}

export default function CVPage() {
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    full_name: "",
    email: "",
    phone: "",
    location: "",
    website: "",
    linkedin: "",
    github: "",
  });

  const [summary, setSummary] = useState("");
  const [experiences, setExperiences] = useState<Experience[]>([
    {
      job_title: "",
      company: "",
      location: "",
      start_date: "",
      end_date: "",
      description: "",
      responsibilities: [""],
    },
  ]);

  const [education, setEducation] = useState<Education[]>([
    {
      degree: "",
      institution: "",
      location: "",
      start_date: "",
      end_date: "",
      gpa: "",
      achievements: [""],
    },
  ]);

  const [skills, setSkills] = useState<Skill[]>([
    { category: "", skills: [""] },
  ]);

  const [format, setFormat] = useState<"docx" | "pdf">("docx");
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string>("");

  const handleGenerate = async () => {
    if (!personalInfo.full_name || !personalInfo.email) {
      alert("Please fill in at least your name and email");
      return;
    }

    setIsGenerating(true);
    setDownloadUrl("");

    try {
      // Clean up data
      const cleanExperiences = experiences
        .filter((exp) => exp.job_title && exp.company)
        .map((exp) => ({
          ...exp,
          responsibilities: exp.responsibilities.filter((r) => r.trim()),
        }));

      const cleanEducation = education
        .filter((edu) => edu.degree && edu.institution)
        .map((edu) => ({
          ...edu,
          achievements: edu.achievements.filter((a) => a.trim()),
        }));

      const cleanSkills = skills
        .filter((skill) => skill.skills.some((s) => s.trim()))
        .map((skill) => ({
          ...skill,
          skills: skill.skills.filter((s) => s.trim()),
        }));

      const response = await fetch("http://localhost:8000/api/v1/cv/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth header when authentication is implemented
          // "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          personal_info: personalInfo,
          summary: summary || undefined,
          experience: cleanExperiences,
          education: cleanEducation,
          skills: cleanSkills,
          format,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "CV generation failed");
      }

      const data = await response.json();
      setDownloadUrl(data.download_url);
    } catch (error: any) {
      console.error("CV generation error:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">CV Builder</h1>
          <p className="text-gray-600">
            Create a professional CV and export as DOCX or PDF
          </p>
        </div>

        {/* Form */}
        <div className="space-y-8">
          {/* Personal Information */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Full Name *"
                value={personalInfo.full_name}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, full_name: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="email"
                placeholder="Email *"
                value={personalInfo.email}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, email: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="tel"
                placeholder="Phone"
                value={personalInfo.phone}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, phone: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Location"
                value={personalInfo.location}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, location: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="url"
                placeholder="Website"
                value={personalInfo.website}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, website: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="LinkedIn"
                value={personalInfo.linkedin}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, linkedin: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="GitHub"
                value={personalInfo.github}
                onChange={(e) =>
                  setPersonalInfo({ ...personalInfo, github: e.target.value })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Professional Summary */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Professional Summary</h2>
            <textarea
              placeholder="Brief overview of your professional background and key strengths..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          {/* Experience - Compact version for token limit */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Experience</h2>
            {experiences.map((exp, expIdx) => (
              <div key={expIdx} className="mb-6 p-4 border border-gray-200 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <input
                    type="text"
                    placeholder="Job Title"
                    value={exp.job_title}
                    onChange={(e) => {
                      const newExp = [...experiences];
                      newExp[expIdx].job_title = e.target.value;
                      setExperiences(newExp);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    placeholder="Company"
                    value={exp.company}
                    onChange={(e) => {
                      const newExp = [...experiences];
                      newExp[expIdx].company = e.target.value;
                      setExperiences(newExp);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    placeholder="Location"
                    value={exp.location}
                    onChange={(e) => {
                      const newExp = [...experiences];
                      newExp[expIdx].location = e.target.value;
                      setExperiences(newExp);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Start (Jan 2020)"
                      value={exp.start_date}
                      onChange={(e) => {
                        const newExp = [...experiences];
                        newExp[expIdx].start_date = e.target.value;
                        setExperiences(newExp);
                      }}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="End (Present)"
                      value={exp.end_date}
                      onChange={(e) => {
                        const newExp = [...experiences];
                        newExp[expIdx].end_date = e.target.value;
                        setExperiences(newExp);
                      }}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <textarea
                  placeholder="Description"
                  value={exp.description}
                  onChange={(e) => {
                    const newExp = [...experiences];
                    newExp[expIdx].description = e.target.value;
                    setExperiences(newExp);
                  }}
                  rows={2}
                  className="w-full mb-2 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
                {exp.responsibilities.map((resp, respIdx) => (
                  <input
                    key={respIdx}
                    type="text"
                    placeholder="• Responsibility"
                    value={resp}
                    onChange={(e) => {
                      const newExp = [...experiences];
                      newExp[expIdx].responsibilities[respIdx] = e.target.value;
                      setExperiences(newExp);
                    }}
                    className="w-full mb-2 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                ))}
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      const newExp = [...experiences];
                      newExp[expIdx].responsibilities.push("");
                      setExperiences(newExp);
                    }}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    + Add Responsibility
                  </button>
                  {experiences.length > 1 && (
                    <button
                      onClick={() => setExperiences(experiences.filter((_, i) => i !== expIdx))}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove Experience
                    </button>
                  )}
                </div>
              </div>
            ))}
            <button
              onClick={() =>
                setExperiences([
                  ...experiences,
                  {
                    job_title: "",
                    company: "",
                    location: "",
                    start_date: "",
                    end_date: "",
                    description: "",
                    responsibilities: [""],
                  },
                ])
              }
              className="flex items-center text-blue-600 hover:text-blue-700"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Experience
            </button>
          </div>

          {/* Format Selection & Generate */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Export</h2>
            <div className="flex items-center space-x-4 mb-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="docx"
                  checked={format === "docx"}
                  onChange={(e) => setFormat(e.target.value as "docx" | "pdf")}
                  className="mr-2"
                />
                DOCX
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="pdf"
                  checked={format === "pdf"}
                  onChange={(e) => setFormat(e.target.value as "docx" | "pdf")}
                  className="mr-2"
                />
                PDF
              </label>
            </div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  <span>Generate CV</span>
                </>
              )}
            </button>
          </div>

          {/* Download Link */}
          {downloadUrl && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-green-900 mb-1">
                    CV Ready!
                  </h3>
                  <p className="text-sm text-green-700">
                    Your CV has been generated successfully
                  </p>
                </div>
                <a
                  href={downloadUrl}
                  download
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
                >
                  <Download className="w-5 h-5" />
                  <span>Download</span>
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

