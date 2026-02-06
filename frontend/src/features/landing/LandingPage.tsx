import { useNavigate } from "react-router-dom";
import { Button } from "../../components/Profile/ui/button";
import { GraduationCap, ArrowRight, BookOpen, Brain, Trophy } from "lucide-react";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col">
            {/* Navbar */}
            <header className="border-b border-border sticky top-0 bg-background/80 backdrop-blur-md z-50">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-2xl text-primary tracking-tight">
                        <span className="bg-primary text-primary-foreground p-1 rounded-lg">LF</span>
                        LEARNFLOW
                    </div>
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" onClick={() => navigate("/login")}>
                            Log in
                        </Button>
                        <Button onClick={() => navigate("/signup")}>
                            Sign up
                        </Button>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <main className="flex-1">
                <section className="py-20 md:py-32 px-4">
                    <div className="container mx-auto max-w-5xl text-center space-y-8">
                        <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                            <GraduationCap className="mr-2 h-4 w-4" />
                            Smart Learning Platform
                        </div>

                        <h1 className="text-4xl md:text-7xl font-bold tracking-tight">
                            Master Your Learning Journey with <span className="text-primary">AI-Powered</span> Tools
                        </h1>

                        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                            Create personalized study plans, track your progress, and boost your knowledge with our intelligent learning assistant.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                            <Button size="lg" className="h-12 px-8 text-lg" onClick={() => navigate("/signup")}>
                                Get Started <ArrowRight className="ml-2 h-5 w-5" />
                            </Button>
                            <Button size="lg" variant="outline" className="h-12 px-8 text-lg" onClick={() => navigate("/login")}>
                                I already have an account
                            </Button>
                        </div>
                    </div>
                </section>

                {/* Features Grid */}
                <section className="py-20 bg-muted/30">
                    <div className="container mx-auto px-4">
                        <div className="grid md:grid-cols-3 gap-8">
                            <div className="bg-card p-8 rounded-2xl border border-border hover:border-primary/50 transition-colors">
                                <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center mb-6">
                                    <BookOpen className="h-6 w-6 text-primary" />
                                </div>
                                <h3 className="text-xl font-bold mb-3">Structured Roadmaps</h3>
                                <p className="text-muted-foreground">Follow clear, step-by-step learning paths designed to take you from beginner to expert.</p>
                            </div>
                            <div className="bg-card p-8 rounded-2xl border border-border hover:border-primary/50 transition-colors">
                                <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center mb-6">
                                    <Brain className="h-6 w-6 text-primary" />
                                </div>
                                <h3 className="text-xl font-bold mb-3">AI Summaries</h3>
                                <p className="text-muted-foreground">Instantly summarize complex topics and generate concise notes to save study time.</p>
                            </div>
                            <div className="bg-card p-8 rounded-2xl border border-border hover:border-primary/50 transition-colors">
                                <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center mb-6">
                                    <Trophy className="h-6 w-6 text-primary" />
                                </div>
                                <h3 className="text-xl font-bold mb-3">Progress Tracking</h3>
                                <p className="text-muted-foreground">Visualize your daily achievements and stay motivated with streak tracking and goals.</p>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="border-t border-border py-8">
                <div className="container mx-auto px-4 text-center text-muted-foreground text-sm">
                    <p>© 2026 LearnFlow. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
