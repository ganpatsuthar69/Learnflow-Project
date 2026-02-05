import React, { useEffect, useState } from "react";
import {
  BookOpen,
  Brain,
  Calendar,
  FileText,
  UserRoundPen,
  ArrowRight,
  Loader2
} from "lucide-react";
import AppLayout from "../../components/AppLayout";
import apiClient from "../../services/apiClient";

interface ProfileData {
  full_name: string;
  // Add other fields if needed for dashboard
}

export default function Dashboard() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await apiClient.get("/profile");
        setProfile(res.data);
      } catch (err) {
        console.error("Failed to fetch profile", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[calc(100vh-100px)]">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      {/* Header Section */}
      <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent">
          {getGreeting()}, {profile?.full_name?.split(" ")[0] || "Student"}!
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Ready to continue your learning journey?
        </p>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Roadmap"
          description="View your personalized learning path."
          icon={<BookOpen className="w-8 h-8 text-blue-500" />}
          path="/roadmap"
          color="bg-blue-500/10 hover:bg-blue-500/20"
          delay={100}
        />

        <DashboardCard
          title="AI Notes"
          description="Summarize & query your study materials."
          icon={<Brain className="w-8 h-8 text-purple-500" />}
          path="/ai-notes"
          color="bg-purple-500/10 hover:bg-purple-500/20"
          delay={200}
        />

        <DashboardCard
          title="Study Plan"
          description="Track your daily and weekly goals."
          icon={<Calendar className="w-8 h-8 text-green-500" />}
          path="/study-plan"
          color="bg-green-500/10 hover:bg-green-500/20"
          delay={300}
        />

        <DashboardCard
          title="Quiz"
          description="Test your knowledge with smart quizzes."
          icon={<FileText className="w-8 h-8 text-orange-500" />}
          path="/quiz"
          color="bg-orange-500/10 hover:bg-orange-500/20"
          delay={400}
        />

        <DashboardCard
          title="Profile"
          description="Manage your account details."
          icon={<UserRoundPen className="w-8 h-8 text-pink-500" />}
          path="/profile"
          color="bg-pink-500/10 hover:bg-pink-500/20"
          delay={500}
        />
      </div>
    </AppLayout>
  );
}

function DashboardCard({
  title,
  description,
  icon,
  path,
  color,
  delay
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  color: string;
  delay: number;
}) {
  return (
    <a
      href={path}
      className={`
        relative group overflow-hidden rounded-2xl p-6 border border-border
        transition-all duration-300 hover:shadow-xl hover:-translate-y-1
        ${color}
        animate-in fade-in zoom-in duration-500 fill-mode-backwards
      `}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="relative z-10 flex flex-col h-full">
        <div className="mb-4 p-3 bg-background rounded-xl w-fit shadow-sm group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>

        <h3 className="text-xl font-semibold mb-2 text-foreground group-hover:text-primary transition-colors">
          {title}
        </h3>

        <p className="text-muted-foreground text-sm mb-6 flex-1">
          {description}
        </p>

        <div className="flex items-center text-sm font-medium text-primary opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
          Get Started <ArrowRight className="ml-2 w-4 h-4" />
        </div>
      </div>

      {/* Decorative gradient blob */}
      <div className="absolute -right-10 -bottom-10 w-32 h-32 bg-current opacity-5 rounded-full blur-3xl group-hover:opacity-10 transition-opacity" />
    </a>
  );
}

