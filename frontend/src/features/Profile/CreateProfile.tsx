import React, { useState } from "react";
import {
  Camera,
  User,
  GraduationCap,
  MapPin,
  AlertCircle,
  ArrowRight,
  Building2,
  Loader2
} from "lucide-react";
import apiClient from "../../services/apiClient";
import axios from "axios";
import { useNavigate } from "react-router-dom";
// Corrected imports pointing to src/components/Profile/ui
import { Button } from "../../components/Profile/ui/button";
import { Input } from "../../components/Profile/ui/input";
import { Label } from "../../components/Profile/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/Profile/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "../../components/Profile/ui/avatar";

interface UserData {
  date_of_birth: string;
  gender: string;
  city: string;
  state: string;
  country: string;
  current_level?: string;
  course_type?: string;
  course_name?: string;
  course_start_year?: string;
  course_end_year?: string;
  current_year?: string;
  institution_name?: string;
}

export default function CreateProfile() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dateError, setDateError] = useState<string | null>(null);

  const [profilePhoto, setProfilePhoto] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const navigate = useNavigate();

  const [formData, setFormData] = useState<UserData>({
    date_of_birth: "",
    gender: "",
    city: "",
    state: "",
    country: "",
  });

  /* ================= DATE HELPERS ================= */
  const getMaxDate = () => {
    const today = new Date();
    today.setFullYear(today.getFullYear() - 10);
    return today.toISOString().split('T')[0];
  };

  const getMinDate = () => {
    const today = new Date();
    today.setFullYear(today.getFullYear() - 120);
    return today.toISOString().split('T')[0];
  };

  /* ================= HANDLERS ================= */
  const handleChange = (field: keyof UserData, value: string) => {
    if (field === "date_of_birth") {
      setDateError(null);
      const selectedDate = new Date(value);
      const today = new Date();
      let age = today.getFullYear() - selectedDate.getFullYear();
      const monthDiff = today.getMonth() - selectedDate.getMonth();
      const dayDiff = today.getDate() - selectedDate.getDate();

      if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) age--;

      if (age < 10) {
        setDateError("You must be at least 10 years old");
        return;
      }
    }
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePhotoSelect = (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      setError("Image size should be less than 5MB");
      return;
    }
    setProfilePhoto(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (dateError) {
      setError("Please fix the date of birth error before submitting");
      window.scrollTo(0, 0);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await apiClient.post("/profile_create", {
        profile: {
          date_of_birth: formData.date_of_birth,
          gender: formData.gender,
          city: formData.city,
          state: formData.state,
          country: formData.country,
        },
        education: {
          current_level: formData.current_level || null,
          course_type: formData.course_type || null,
          course_name: formData.course_name || null,
          course_start_year: formData.course_start_year || null,
          course_end_year: formData.course_end_year || null,
          current_year: formData.current_year || null,
          institution_name: formData.institution_name || null,
        },
      });

      if (profilePhoto) {
        const fd = new FormData();
        fd.append("file", profilePhoto);
        await apiClient.post("/profile/photo", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      navigate("/dashboard");

    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === "string") setError(detail);
        else if (Array.isArray(detail)) setError(detail.map((e: { msg: string }) => e.msg).join(", "));
        else setError("Failed to create profile");
      } else {
        setError("Something went wrong. Please try again.");
      }
      window.scrollTo(0, 0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex items-center justify-center p-4 py-12">
      {/* Background Shapes */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-4xl w-full relative z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent mb-4 tracking-tight">
            Setup Your Profile
          </h1>
          <p className="text-xl text-muted-foreground">Tell us a bit about yourself to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-xl flex items-center gap-3 animate-in shake">
              <AlertCircle className="w-5 h-5" /> {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Left Column: Photo */}
            <div className="lg:col-span-1">
              <div className="bg-card/50 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-xl text-center sticky top-8">
                <div className="relative group mx-auto w-40 h-40 mb-6">
                  <Avatar className="w-full h-full border-4 border-background shadow-2xl">
                    <AvatarImage src={previewUrl || undefined} className="object-cover" />
                    <AvatarFallback className="text-4xl bg-muted"><User className="w-16 h-16 text-muted-foreground/50" /></AvatarFallback>
                  </Avatar>

                  <label htmlFor="photo-upload" className="absolute bottom-2 right-2 p-3 bg-primary text-primary-foreground rounded-full cursor-pointer hover:bg-primary/90 shadow-lg transition-transform hover:scale-110 active:scale-95">
                    <Camera className="w-5 h-5" />
                    <input
                      id="photo-upload"
                      type="file"
                      accept="image/png,image/jpeg,image/jpg"
                      className="hidden"
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => e.target.files && handlePhotoSelect(e.target.files[0])}
                    />
                  </label>
                </div>
                <h3 className="text-lg font-semibold mb-1">Profile Photo</h3>
                <p className="text-sm text-muted-foreground">Optional. Surfaces your friendly face!</p>
              </div>
            </div>

            {/* Right Column: Details */}
            <div className="lg:col-span-2 space-y-6">

              {/* Personal Info Card */}
              <div className="bg-card/80 backdrop-blur-sm border border-border/50 rounded-3xl p-8 shadow-sm">
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-foreground">
                  <User className="w-5 h-5 text-blue-500" /> Personal Information
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="after:content-['*'] after:ml-0.5 after:text-destructive">Date of Birth</Label>
                    <Input
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("date_of_birth", e.target.value)}
                      max={getMaxDate()}
                      min={getMinDate()}
                      required
                      className={dateError ? "border-destructive bg-destructive/5" : ""}
                    />
                    {dateError && <p className="text-xs text-destructive">{dateError}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label className="after:content-['*'] after:ml-0.5 after:text-destructive">Gender</Label>
                    <Select value={formData.gender} onValueChange={(v: string) => handleChange("gender", v)} required>
                      <SelectTrigger><SelectValue placeholder="Select Gender" /></SelectTrigger>
                      <SelectContent>
                        {["Male", "Female", "Other", "Prefer not to say"].map(o => (
                          <SelectItem key={o} value={o}>{o}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 relative">
                    <Label className="after:content-['*'] after:ml-0.5 after:text-destructive">City</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                      <Input className="pl-9" placeholder="New York" value={formData.city} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("city", e.target.value)} required />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="after:content-['*'] after:ml-0.5 after:text-destructive">State</Label>
                    <Input placeholder="NY" value={formData.state} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("state", e.target.value)} required />
                  </div>

                  <div className="md:col-span-2 space-y-2">
                    <Label className="after:content-['*'] after:ml-0.5 after:text-destructive">Country</Label>
                    <Input placeholder="United States" value={formData.country} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("country", e.target.value)} required />
                  </div>
                </div>
              </div>

              {/* Education Card */}
              <div className="bg-card/80 backdrop-blur-sm border border-border/50 rounded-3xl p-8 shadow-sm">
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-foreground">
                  <GraduationCap className="w-5 h-5 text-purple-500" /> Education (Optional)
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Current Level</Label>
                    <Select value={formData.current_level || ""} onValueChange={(v: string) => handleChange("current_level", v)}>
                      <SelectTrigger><SelectValue placeholder="Select Level" /></SelectTrigger>
                      <SelectContent>
                        {["School", "College", "Employee", "Other"].map(o => (
                          <SelectItem key={o} value={o}>{o}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Course Type</Label>
                    <Select value={formData.course_type || ""} onValueChange={(v: string) => handleChange("course_type", v)}>
                      <SelectTrigger><SelectValue placeholder="Select Type" /></SelectTrigger>
                      <SelectContent>
                        {["School", "Graduation", "Post Graduation", "Other"].map(o => (
                          <SelectItem key={o} value={o}>{o}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="md:col-span-2 space-y-2">
                    <Label>Course Name</Label>
                    <Input placeholder="e.g. Computer Science" value={formData.course_name || ""} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("course_name", e.target.value)} />
                  </div>

                  <div className="space-y-2">
                    <Label>Start Year</Label>
                    <Input type="number" placeholder="YYYY" value={formData.course_start_year || ""} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("course_start_year", e.target.value)} />
                  </div>

                  <div className="space-y-2">
                    <Label>End Year</Label>
                    <Input type="number" placeholder="YYYY" value={formData.course_end_year || ""} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("course_end_year", e.target.value)} />
                  </div>

                  <div className="space-y-2">
                    <Label>Current Year</Label>
                    <Input placeholder="e.g. Final Year" value={formData.current_year || ""} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("current_year", e.target.value)} />
                  </div>

                  <div className="md:col-span-2 space-y-2">
                    <Label>Institution</Label>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                      <Input className="pl-9" placeholder="University Name" value={formData.institution_name || ""} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange("institution_name", e.target.value)} />
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <div className="flex justify-end gap-4 pt-4 border-t border-border">
            <Button type="button" variant="ghost" onClick={() => window.history.back()} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" size="lg" disabled={loading || !!dateError} className="px-8 shadow-lg shadow-primary/25">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Creating...
                </>
              ) : (
                <>
                  Complete Setup <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}