import React, { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "./ui/select";
import {
  Loader2,
  Upload,
  User,
  MapPin,
  Building2,
  GraduationCap,
  Save,
  X,
  Mail,
  CheckCircle2,
  AlertCircle,
  Edit3
} from "lucide-react";
import apiClient from "../../services/apiClient";

interface UserData {
  profile_photo_url: string | null;
  username: string;
  full_name: string;
  email: string;
  date_of_birth: string | null;
  gender: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  current_level?: string | null;
  course_type?: string | null;
  course_name?: string | null;
  course_start_year?: string | null;
  course_end_year?: string | null;
  current_year?: string | null;
  institution_name?: string | null;
}

interface EditProfileProps {
  onCancel: () => void;
  onSaveComplete: () => void;
}

export default function EditProfile({ onCancel, onSaveComplete }: EditProfileProps) {
  const [formData, setFormData] = useState<UserData | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);

  // Email OTP states
  const [newEmail, setNewEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  // UI states
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await apiClient.get("/profile");
        setFormData(res.data);

        if (res.data.profile_photo_url) {
          try {
            const photoRes = await apiClient.get("/profile/photo");
            setPhotoPreview(photoRes.data.url);
          } catch {
            console.log("No profile photo");
          }
        }
      } catch {
        setError("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (field: keyof UserData, value: string) => {
    setFormData(prev => prev ? { ...prev, [field]: value } : null);
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        setError("Please upload a JPG or PNG image");
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        setError("Image must be less than 5MB");
        return;
      }

      setError(null);
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const requestEmailOtp = async () => {
    if (!newEmail) {
      setError("Enter new email");
      return;
    }

    setEmailLoading(true);
    setError(null);

    try {
      await apiClient.patch("/profile/email/request", { email: newEmail });
      setOtpSent(true);
      setSuccess("OTP sent to new email");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "Failed to send OTP");
    } finally {
      setEmailLoading(false);
    }
  };

  const verifyEmailOtp = async () => {
    if (!otp) {
      setError("Enter OTP");
      return;
    }

    setEmailLoading(true);
    setError(null);

    try {
      await apiClient.post("/profile/email/verify", {
        email: newEmail,
        otp,
      });

      const res = await apiClient.get("/profile");
      setFormData(res.data);

      setOtp("");
      setNewEmail("");
      setOtpSent(false);
      setSuccess("Email updated successfully");

    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "OTP verification failed");
    } finally {
      setEmailLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      if (photoFile) {
        const formDataUpload = new FormData();
        formDataUpload.append("file", photoFile);
        await apiClient.post("/profile/photo", formDataUpload, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      await apiClient.patch("/profile_update", {
        profile: {
          full_name: formData.full_name,
          date_of_birth: formData.date_of_birth,
          gender: formData.gender,
          city: formData.city,
          state: formData.state,
          country: formData.country,
        },
        education: {
          current_level: formData.current_level,
          course_type: formData.course_type,
          course_name: formData.course_name,
          course_start_year: formData.course_start_year,
          course_end_year: formData.course_end_year,
          current_year: formData.current_year,
          institution_name: formData.institution_name,
        },
      });

      setSuccess("Profile updated successfully!");

      setTimeout(() => {
        onSaveComplete();
      }, 1000);

    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 min-h-[50vh]">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground animate-pulse">Loading data...</p>
      </div>
    );
  }

  if (!formData) return null;

  return (
    <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Header Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card border border-border p-6 rounded-3xl shadow-sm">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Edit3 className="w-6 h-6 text-primary" /> Edit Profile
          </h2>
          <p className="text-muted-foreground text-sm mt-1">Update your personal and educational details</p>
        </div>
        <div className="flex items-center gap-3">
          <Button type="button" variant="outline" onClick={onCancel} disabled={saving}>
            <X className="w-4 h-4 mr-2" /> Cancel
          </Button>
          <Button type="submit" disabled={saving} className="bg-primary text-primary-foreground hover:bg-primary/90">
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-xl flex items-center gap-3 animate-in shake">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      )}

      {success && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 p-4 rounded-xl flex items-center gap-3 animate-in fade-in">
          <CheckCircle2 className="w-5 h-5" /> {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left Column: Photo & Basic Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Photo Card */}
          <div className="bg-card border border-border rounded-3xl p-6 shadow-sm flex flex-col items-center text-center">
            <div className="relative group">
              <Avatar className="h-32 w-32 border-4 border-background shadow-lg mb-4">
                <AvatarImage src={photoPreview || undefined} alt={formData.full_name} className="object-cover" />
                <AvatarFallback className="text-4xl">{formData.full_name[0]}</AvatarFallback>
              </Avatar>
              <Label htmlFor="photo-upload" className="absolute bottom-4 right-0 p-2 bg-primary text-white rounded-full cursor-pointer hover:bg-primary/90 shadow-md transition-all hover:scale-105">
                <Upload className="w-4 h-4" />
              </Label>
              <Input id="photo-upload" type="file" accept="image/jpeg,image/png" className="hidden" onChange={handlePhotoChange} />
            </div>
            <p className="text-sm text-muted-foreground">Allowed *.jpeg, *.jpg, *.png, max 5MB</p>

            <div className="w-full mt-6 space-y-4 text-left">
              <div className="space-y-2">
                <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Full Name</Label>
                <Input value={formData.full_name} disabled className="bg-muted/50 border-transparent font-medium" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Username</Label>
                <Input value={formData.username} disabled className="bg-muted/50 border-transparent" />
              </div>
            </div>
          </div>

          {/* Email Section */}
          <div className="bg-card border border-border rounded-3xl p-6 shadow-sm space-y-4">
            <h3 className="font-semibold flex items-center gap-2"><Mail className="w-4 h-4 text-blue-500" /> Email Settings</h3>
            <div className="space-y-3">
              <Input
                value={newEmail || formData.email}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="new@email.com"
              />
              <Button
                type="button"
                onClick={requestEmailOtp}
                disabled={emailLoading || !newEmail || newEmail === formData.email}
                variant="secondary"
                size="sm"
                className="w-full"
              >
                {emailLoading && !otpSent ? <Loader2 className="w-3 h-3 animate-spin mr-2" /> : null}
                {otpSent ? "Resend OTP" : "Request Change"}
              </Button>

              {otpSent && (
                <div className="pt-2 space-y-2 animate-in slide-in-from-top-2">
                  <Input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Enter 6-digit OTP" />
                  <Button type="button" onClick={verifyEmailOtp} disabled={emailLoading} size="sm" className="w-full">
                    {emailLoading ? "Verifying..." : "Verify & Update"}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Forms */}
        <div className="lg:col-span-2 space-y-6">

          {/* Personal Details */}
          <div className="bg-card border border-border rounded-3xl p-8 shadow-sm">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-foreground">
              <User className="w-5 h-5 text-blue-500" /> Personal Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="dob">Date of Birth</Label>
                <Input id="dob" type="date" value={formData.date_of_birth || ""} onChange={(e) => handleChange('date_of_birth', e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Gender</Label>
                <Select value={formData.gender || ""} onValueChange={(v) => handleChange('gender', v)}>
                  <SelectTrigger><SelectValue placeholder="Select Gender" /></SelectTrigger>
                  <SelectContent>
                    {["Male", "Female", "Other", "Prefer not to say"].map(o => (
                      <SelectItem key={o} value={o}>{o}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>City</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                  <Input className="pl-9" value={formData.city || ""} onChange={(e) => handleChange('city', e.target.value)} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>State</Label>
                <Input value={formData.state || ""} onChange={(e) => handleChange('state', e.target.value)} />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>Country</Label>
                <Input value={formData.country || ""} onChange={(e) => handleChange('country', e.target.value)} />
              </div>
            </div>
          </div>

          {/* Education Details */}
          <div className="bg-card border border-border rounded-3xl p-8 shadow-sm">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-foreground">
              <GraduationCap className="w-5 h-5 text-purple-500" /> Education Check
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Current Level</Label>
                <Select value={formData.current_level || ""} onValueChange={(v) => handleChange('current_level', v)}>
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
                <Select value={formData.course_type || ""} onValueChange={(v) => handleChange('course_type', v)}>
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
                <Input placeholder="e.g. Computer Science" value={formData.course_name || ""} onChange={(e) => handleChange('course_name', e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>Start Year</Label>
                <Input type="number" placeholder="YYYY" value={formData.course_start_year || ""} onChange={(e) => handleChange('course_start_year', e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>End Year</Label>
                <Input type="number" placeholder="YYYY" value={formData.course_end_year || ""} onChange={(e) => handleChange('course_end_year', e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>Current Year</Label>
                <Input placeholder="e.g. Final Year" value={formData.current_year || ""} onChange={(e) => handleChange('current_year', e.target.value)} />
              </div>

              <div className="md:col-span-2 space-y-2">
                <Label>Institution Name</Label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                  <Input className="pl-9" placeholder="University / School Name" value={formData.institution_name || ""} onChange={(e) => handleChange('institution_name', e.target.value)} />
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </form>
  );
}