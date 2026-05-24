import React, { useEffect, useState } from "react";
import apiClient from "../../services/apiClient";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
  User,
  MapPin,
  Calendar,
  Mail,
  GraduationCap,
  Building2,
  Clock,
  Edit3,
  Loader2,
  Globe2
} from "lucide-react";

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

export default function ProfileView({ onEdit }: { onEdit: () => void }) {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get("/profile");
        setUserData(res.data);

        if (res.data.profile_photo_url) {
          try {
            const photoRes = await apiClient.get("/profile/photo");
            setPhotoUrl(photoRes.data.url);
          } catch {
            console.log("No profile photo");
          }
        }
      } catch (err: unknown) {
        const error = err as { response?: { status: number } };
        if (error.response?.status === 404) {
          setError("PROFILE_NOT_FOUND");
        } else {
          setError("Failed to load profile");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 min-h-[50vh]">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground animate-pulse">Loading profile...</p>
      </div>
    );
  }

  if (error === "PROFILE_NOT_FOUND") {
    return (
      <div className="flex flex-col items-center justify-center text-center p-8 bg-card border border-border rounded-3xl shadow-sm max-w-md mx-auto mt-10">
        <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mb-6">
          <User className="w-10 h-10 text-muted-foreground" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Profile Not Found</h2>
        <p className="text-muted-foreground mb-6">Start your journey by creating your profile today.</p>
        <Button onClick={() => (window.location.href = "/createprofile")} size="lg" className="w-full">
          Create Profile
        </Button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-8 bg-destructive/5 border border-destructive/20 rounded-3xl max-w-md mx-auto mt-10">
        <h3 className="text-lg font-semibold text-destructive mb-2">Error Loading Profile</h3>
        <p className="text-muted-foreground">{error}</p>
        <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!userData) return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-700">

      {/* Hero / Header Card */}
      <div className="relative overflow-hidden glass-panel interactive-hover rounded-3xl">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-emerald-500/10 to-teal-500/10 opacity-50" />

        <div className="relative z-10 p-8 flex flex-col md:flex-row items-center gap-8">
          <Avatar className="h-32 w-32 border-4 border-background shadow-xl ring-4 ring-primary/10">
            <AvatarImage src={photoUrl || undefined} alt={userData.full_name} className="object-cover" />
            <AvatarFallback className="text-4xl font-bold bg-primary text-primary-foreground">
              {userData.full_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 text-center md:text-left space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
              {userData.full_name}
            </h1>
            <p className="text-lg text-muted-foreground flex items-center justify-center md:justify-start gap-2">
              <span className="font-semibold text-primary">@{userData.username}</span>
              <span>•</span>
              <span className="flex items-center gap-1"><Mail className="w-4 h-4" /> {userData.email}</span>
            </p>
          </div>

          <Button onClick={onEdit} size="lg" className="shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 bg-primary text-primary-foreground hover:bg-primary/90">
            <Edit3 className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Personal Info */}
        <div className="md:col-span-1 space-y-6">
          <section className="glass-panel interactive-hover rounded-3xl p-6 h-full">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-primary">
              <User className="w-5 h-5" /> Personal Details
            </h3>

            <div className="space-y-4">
              <InfoRow icon={<Calendar className="text-primary" />} label="Birthday" value={userData.date_of_birth} />
              <InfoRow icon={<User className="text-primary" />} label="Gender" value={userData.gender} />
              <InfoRow icon={<MapPin className="text-primary" />} label="City" value={userData.city} />
              <InfoRow icon={<Globe2 className="text-primary" />} label="Region" value={[userData.state, userData.country].filter(Boolean).join(", ")} />
            </div>
          </section>
        </div>

        {/* Education Info */}
        <div className="md:col-span-2 space-y-6">
          {userData.current_level || userData.institution_name ? (
            <section className="glass-panel interactive-hover rounded-3xl p-6 h-full relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-bl-full -mr-8 -mt-8" />

              <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-primary">
                <GraduationCap className="w-5 h-5" /> Education
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <InfoCard
                  title="Institution"
                  value={userData.institution_name}
                  icon={<Building2 className="w-5 h-5 text-emerald-500" />}
                  fullWidth
                />

                <InfoCard
                  title="Current Level"
                  value={userData.current_level}
                  icon={<GraduationCap className="w-5 h-5 text-teal-500" />}
                />

                <InfoCard
                  title="Course"
                  value={userData.course_name}
                  subValue={userData.course_type}
                  icon={<User className="w-5 h-5 text-green-500" />}
                />

                <InfoCard
                  title="Duration"
                  value={userData.course_start_year && userData.course_end_year ? `${userData.course_start_year} - ${userData.course_end_year}` : null}
                  icon={<Clock className="w-5 h-5 text-emerald-400" />}
                />

                <InfoCard
                  title="Current Year"
                  value={userData.current_year}
                  icon={<Calendar className="w-5 h-5 text-teal-400" />}
                />
              </div>
            </section>
          ) : (
            <div className="bg-muted/50 border-2 border-dashed border-border rounded-3xl p-8 flex flex-col items-center justify-center text-center h-full min-h-[200px]">
              <GraduationCap className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
              <p className="font-medium text-muted-foreground">No education details added yet.</p>
              <Button variant="link" onClick={onEdit} className="text-primary font-bold">Add Details</Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ icon, label, value }: { icon: React.ReactNode, label: string, value: string | null | undefined }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/5 transition-colors group cursor-default">
      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
        {React.cloneElement(icon as React.ReactElement<{ size: number }>, { size: 14 })}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground font-medium group-hover:text-primary transition-colors">{label}</p>
        <p className="text-sm font-medium truncate">{value || "Not provided"}</p>
      </div>
    </div>
  );
}

function InfoCard({ icon, title, value, subValue, fullWidth }: { icon: React.ReactNode, title: string, value: string | null | undefined, subValue?: string | null | undefined, fullWidth?: boolean }) {
  if (!value) return null;

  return (
    <div className={`bg-background/40 p-4 rounded-2xl border border-border/50 hover:border-primary/50 transition-all hover:shadow-md hover:-translate-y-1 ${fullWidth ? 'col-span-1 sm:col-span-2' : ''}`}>
      <div className="flex items-start gap-3">
        <div className="p-2 bg-background rounded-lg shadow-sm">
          {icon}
        </div>
        <div>
          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">{title}</p>
          <p className="font-semibold text-foreground">{value}</p>
          {subValue && <p className="text-sm text-muted-foreground">{subValue}</p>}
        </div>
      </div>
    </div>
  );
}