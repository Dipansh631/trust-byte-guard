import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Mail, Image, BarChart3, AlertTriangle, CheckCircle } from "lucide-react";
import EmailAnalyzer from "@/components/EmailAnalyzer";
import DeepfakeDetector from "@/components/DeepfakeDetector";
import AnalysisComplete from "@/components/AnalysisComplete";
import { toast } from "@/hooks/use-toast";

interface AnalysisHistory {
  id: string;
  type: 'email' | 'deepfake';
  timestamp: Date;
  result: {
    label: string;
    confidence: number;
    trust_score: number;
    suspicious_phrases?: string[];
    reason_analysis: string;
  };
}

const Index = () => {
  const [activeTab, setActiveTab] = useState("email");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [showCompletion, setShowCompletion] = useState(false);
  const [lastAnalysisType, setLastAnalysisType] = useState<'email' | 'deepfake' | null>(null);
  const [stats, setStats] = useState({
    totalScans: 0,
    phishingDetected: 0,
    deepfakesFound: 0,
    safeContent: 0
  });

  // Load analysis history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('cyberguard-analysis-history');
    if (savedHistory) {
      const parsed = JSON.parse(savedHistory);
      setAnalysisHistory(parsed.map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp)
      })));
    }
  }, []);

  // Update stats when history changes
  useEffect(() => {
    const newStats = {
      totalScans: analysisHistory.length,
      phishingDetected: analysisHistory.filter(h => h.type === 'email' && h.result.label === 'Phishing').length,
      deepfakesFound: analysisHistory.filter(h => h.type === 'deepfake' && h.result.label === 'Deepfake').length,
      safeContent: analysisHistory.filter(h => h.result.label === 'Safe' || h.result.label === 'Real').length
    };
    setStats(newStats);
  }, [analysisHistory]);

  const saveAnalysisToHistory = (type: 'email' | 'deepfake', result: any) => {
    const newAnalysis: AnalysisHistory = {
      id: Date.now().toString(),
      type,
      timestamp: new Date(),
      result: {
        label: result.label,
        confidence: result.confidence,
        trust_score: result.trust_score,
        suspicious_phrases: result.suspicious_phrases,
        reason_analysis: result.reason_analysis
      }
    };

    const updatedHistory = [newAnalysis, ...analysisHistory];
    setAnalysisHistory(updatedHistory);
    
    // Save to localStorage
    localStorage.setItem('cyberguard-analysis-history', JSON.stringify(updatedHistory));
  };

  const handleEmailAnalysis = async (emailData: { subject: string; body: string }) => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('http://localhost:8000/analyze/email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      saveAnalysisToHistory('email', result);
      setLastAnalysisType('email');
      setShowCompletion(true);
      
      toast({
        title: "Email Analysis Complete",
        description: `Detected: ${result.label} (${result.confidence}% confidence)`,
      });
    } catch (error) {
      console.error('Email analysis error:', error);
      
      // Check if it's a connection error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        toast({
          title: "Backend Server Not Running",
          description: "Please start the backend server at localhost:8000. Using demo mode for now.",
          variant: "destructive",
        });
        
        // Use demo data when backend is not available
        const demoResult = {
          label: emailData.subject.toLowerCase().includes('urgent') ? 'Phishing' : 'Safe',
          confidence: emailData.subject.toLowerCase().includes('urgent') ? 85 : 15,
          trust_score: emailData.subject.toLowerCase().includes('urgent') ? 85 : 15,
          suspicious_phrases: emailData.subject.toLowerCase().includes('urgent') ? ['urgent'] : [],
          reason_analysis: emailData.subject.toLowerCase().includes('urgent') 
            ? 'High confidence phishing detection. Detected suspicious phrases: urgent. This email contains characteristics commonly found in phishing attempts.'
            : 'Email appears to be legitimate. No suspicious patterns detected.'
        };
        
        saveAnalysisToHistory('email', demoResult);
        setLastAnalysisType('email');
        setShowCompletion(true);
        toast({
          title: "Email Analysis Complete (Demo Mode)",
          description: `Detected: ${demoResult.label} (${demoResult.confidence}% confidence)`,
        });
        return;
      }
      
      toast({
        title: "Analysis Failed",
        description: "Could not analyze email. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeepfakeAnalysis = async (file: File) => {
    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/analyze/media', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      saveAnalysisToHistory('deepfake', result);
      setLastAnalysisType('deepfake');
      setShowCompletion(true);
      
      toast({
        title: "Media Analysis Complete",
        description: `Detected: ${result.label} (${result.confidence}% confidence)`,
      });
    } catch (error) {
      console.error('Deepfake analysis error:', error);
      
      // Check if it's a connection error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        toast({
          title: "Backend Server Not Running",
          description: "Please start the backend server at localhost:8000. Using demo mode for now.",
          variant: "destructive",
        });
        
        // Use demo data when backend is not available
        const isVideo = file.type.startsWith('video/');
        const demoResult = {
          label: Math.random() > 0.7 ? 'Deepfake' : 'Real',
          confidence: Math.floor(Math.random() * 40) + 30, // 30-70% confidence
          trust_score: Math.floor(Math.random() * 40) + 30,
          reason_analysis: Math.random() > 0.7 
            ? 'Moderate confidence deepfake detection. The media shows characteristics commonly associated with AI-generated or manipulated content.'
            : 'Media appears to be authentic. No significant signs of manipulation detected.',
          frames_analyzed: isVideo ? Math.floor(Math.random() * 20) + 10 : undefined
        };
        
        saveAnalysisToHistory('deepfake', demoResult);
        setLastAnalysisType('deepfake');
        setShowCompletion(true);
        toast({
          title: "Media Analysis Complete (Demo Mode)",
          description: `Detected: ${demoResult.label} (${demoResult.confidence}% confidence)`,
        });
        return;
      }
      
      toast({
        title: "Analysis Failed",
        description: "Could not analyze media. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyzeAnother = () => {
    setShowCompletion(false);
    setLastAnalysisType(null);
    // The individual components will handle clearing their forms
  };

  const handleClearForm = () => {
    setShowCompletion(false);
    setLastAnalysisType(null);
    // The individual components will handle clearing their forms
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Shield className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">CyberGuard</h1>
                <p className="text-sm text-muted-foreground">AI-Powered Security Detection</p>
              </div>
            </div>
            
            {/* Stats Summary */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">{stats.totalScans}</div>
                <div className="text-xs text-muted-foreground">Total Scans</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-destructive">{stats.phishingDetected + stats.deepfakesFound}</div>
                <div className="text-xs text-muted-foreground">Threats Found</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.safeContent}</div>
                <div className="text-xs text-muted-foreground">Safe Content</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 max-w-md mx-auto">
            <TabsTrigger value="email" className="flex items-center space-x-2">
              <Mail className="w-4 h-4" />
              <span>Email Phishing</span>
            </TabsTrigger>
            <TabsTrigger value="deepfake" className="flex items-center space-x-2">
              <Image className="w-4 h-4" />
              <span>Deepfake Detection</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="email" className="space-y-6">
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold">Email Phishing Detector</h2>
              <p className="text-muted-foreground">
                Analyze email content for suspicious patterns and phishing attempts
              </p>
            </div>
            <EmailAnalyzer 
              onAnalyze={handleEmailAnalysis}
              isAnalyzing={isAnalyzing}
              onClearForm={handleClearForm}
            />
          </TabsContent>

          <TabsContent value="deepfake" className="space-y-6">
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold">Deepfake Media Detector</h2>
              <p className="text-muted-foreground">
                Upload images or videos to detect AI-generated or manipulated content
              </p>
            </div>
            <DeepfakeDetector 
              onAnalyze={handleDeepfakeAnalysis}
              isAnalyzing={isAnalyzing}
              onClearForm={handleClearForm}
            />
          </TabsContent>
        </Tabs>

        {/* Analysis Complete Message */}
        {showCompletion && lastAnalysisType && (
          <div className="max-w-4xl mx-auto mt-6">
            <AnalysisComplete
              type={lastAnalysisType}
              onAnalyzeAnother={handleAnalyzeAnother}
              onClearForm={handleClearForm}
            />
          </div>
        )}

        {/* Recent Analysis History */}
        {analysisHistory.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5" />
                <span>Recent Analysis</span>
              </CardTitle>
              <CardDescription>
                Your recent security scans and their results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisHistory.slice(0, 5).map((analysis) => (
                  <div key={analysis.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      {analysis.type === 'email' ? (
                        <Mail className="w-5 h-5 text-blue-500" />
                      ) : (
                        <Image className="w-5 h-5 text-purple-500" />
                      )}
                      <div>
                        <div className="font-medium">
                          {analysis.type === 'email' ? 'Email Analysis' : 'Media Analysis'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {analysis.timestamp.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={analysis.result.label === 'Phishing' || analysis.result.label === 'Deepfake' ? 'destructive' : 'default'}
                      >
                        {analysis.result.label}
                      </Badge>
                      <div className="text-sm font-medium">
                        {analysis.result.confidence}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default Index;