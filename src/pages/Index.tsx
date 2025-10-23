import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Shield, Mail, Image, BarChart3, AlertTriangle, CheckCircle, FileText } from "lucide-react";
import { Link } from "react-router-dom";
import EmailAnalyzer from "@/components/EmailAnalyzer";
import DeepfakeDetector from "@/components/DeepfakeDetector";
import AnalysisComplete from "@/components/AnalysisComplete";
import { toast } from "@/hooks/use-toast";
import { getApiBase, healthCheck } from "@/lib/api";

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
  const [currentDeepfakeResult, setCurrentDeepfakeResult] = useState<any>(null);
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
      deepfakesFound: analysisHistory.filter(h => h.type === 'deepfake' && h.result.label === 'AI-Generated').length,
      safeContent: analysisHistory.filter(h => h.result.label === 'Safe' || h.result.label === 'Human-Created').length
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

  const createReport = async (analysisData: any, type: string) => {
    try {
      const response = await fetch(`${getApiBase()}/reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          analysis_data: analysisData,
          user_notes: ''
        }),
      });

      if (response.ok) {
        console.log('Report created successfully');
      } else {
        console.log('Report endpoint not available, skipping report creation');
      }
    } catch (error) {
      // Silently handle report creation errors - this is not critical functionality
      console.log('Report creation skipped (endpoint not available)');
    }
  };

  const handleEmailAnalysis = async (emailData: { subject: string; body: string }) => {
    setIsAnalyzing(true);
    
    try {
      const isUp = await healthCheck(800);
      if (!isUp) {
        throw new TypeError('Failed to fetch');
      }
      const response = await fetch(`${getApiBase()}/analyze/email`, {
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
      
      // Create report automatically (non-blocking)
      createReport(result, 'email').catch(() => {
        // Silently handle report creation errors
      });
      
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
          description: `Backend not reachable at ${getApiBase()}. Using demo mode for now.`,
          variant: "destructive",
        });
        
        // Use demo data when backend is not available
        const subjectLower = emailData.subject.toLowerCase();
        const bodyLower = emailData.body.toLowerCase();
        const fullText = `${emailData.subject} ${emailData.body}`.toLowerCase();
        
        // Analyze for phishing indicators
        const urgencyWords = ['urgent', 'immediately', 'asap', 'right now', 'act now', 'limited time'];
        const authorityWords = ['verify', 'confirm', 'update', 'validate', 'security alert', 'account locked'];
        const financialWords = ['free money', 'prize', 'winner', 'congratulations', 'lottery'];
        const actionWords = ['click here', 'click now', 'verify now', 'reset password'];
        const threatWords = ['account will be closed', 'permanent suspension', 'legal action'];
        
        const urgencyScore = urgencyWords.filter(word => fullText.includes(word)).length;
        const authorityScore = authorityWords.filter(word => fullText.includes(word)).length;
        const financialScore = financialWords.filter(word => fullText.includes(word)).length;
        const actionScore = actionWords.filter(word => fullText.includes(word)).length;
        const threatScore = threatWords.filter(word => fullText.includes(word)).length;
        
        const totalSuspiciousScore = urgencyScore + authorityScore + financialScore + actionScore + threatScore;
        const hasUrls = fullText.includes('http') || fullText.includes('www.');
        const hasExclamation = (emailData.subject + emailData.body).split('!').length > 3;
        
        const isPhishing = totalSuspiciousScore >= 2 || (urgencyScore >= 1 && hasUrls);
        const confidence = isPhishing ? Math.min(95, 50 + (totalSuspiciousScore * 15) + (hasUrls ? 20 : 0) + (hasExclamation ? 10 : 0)) : Math.max(5, 50 - (totalSuspiciousScore * 10));
        
        const suspiciousPhrases = [];
        if (urgencyScore > 0) suspiciousPhrases.push(...urgencyWords.filter(word => fullText.includes(word)));
        if (authorityScore > 0) suspiciousPhrases.push(...authorityWords.filter(word => fullText.includes(word)));
        if (financialScore > 0) suspiciousPhrases.push(...financialWords.filter(word => fullText.includes(word)));
        if (actionScore > 0) suspiciousPhrases.push(...actionWords.filter(word => fullText.includes(word)));
        if (threatScore > 0) suspiciousPhrases.push(...threatWords.filter(word => fullText.includes(word)));
        
        const demoResult = {
          label: isPhishing ? 'Phishing' : 'Safe',
          confidence: Math.round(confidence),
          trust_score: Math.round(confidence),
          suspicious_phrases: [...new Set(suspiciousPhrases)], // Remove duplicates
          reason_analysis: isPhishing 
            ? `High confidence phishing detection. Detected ${totalSuspiciousScore} suspicious patterns. This email contains characteristics commonly found in phishing attempts.`
            : 'Email appears to be legitimate. No suspicious patterns detected.',
          detailed_analysis: {
            overall_assessment: {
              label: isPhishing ? 'Phishing' : 'Safe',
              confidence: Math.round(confidence),
              risk_level: confidence >= 80 ? 'HIGH RISK' : confidence >= 60 ? 'MEDIUM RISK' : confidence >= 40 ? 'LOW RISK' : 'SAFE',
              summary: isPhishing 
                ? `This email shows ${totalSuspiciousScore > 3 ? 'STRONG' : totalSuspiciousScore > 1 ? 'MODERATE' : 'WEAK'} indicators of phishing with ${totalSuspiciousScore} suspicious patterns detected.`
                : 'This email appears to be legitimate with minimal suspicious patterns detected.'
            },
            pattern_analysis: {
              urgency_indicators: {
                score: urgencyScore,
                patterns_found: urgencyWords.filter(word => fullText.includes(word)),
                explanation: 'High urgency language is commonly used in phishing emails to pressure victims into quick action.'
              },
              authority_claims: {
                score: authorityScore,
                patterns_found: authorityWords.filter(word => fullText.includes(word)),
                explanation: 'Phishing emails often impersonate legitimate authorities or institutions.'
              },
              financial_incentives: {
                score: financialScore,
                patterns_found: financialWords.filter(word => fullText.includes(word)),
                explanation: 'Offers of money, prizes, or financial benefits are common phishing tactics.'
              },
              action_requirements: {
                score: actionScore,
                patterns_found: actionWords.filter(word => fullText.includes(word)),
                explanation: 'Phishing emails typically require immediate action from the victim.'
              },
              social_engineering: {
                score: 0,
                patterns_found: [],
                explanation: 'Trust-building language is used to make phishing attempts appear legitimate.'
              },
              threats_and_pressure: {
                score: threatScore,
                patterns_found: threatWords.filter(word => fullText.includes(word)),
                explanation: 'Threats of account closure or legal action are common phishing tactics.'
              }
            },
            technical_analysis: {
              urls_and_links: {
                total_urls: hasUrls ? 1 : 0,
                suspicious_urls: hasUrls ? ['suspicious link detected'] : [],
                shortened_urls: [],
                explanation: 'Suspicious or shortened URLs are often used to hide malicious destinations.'
              },
              email_structure: {
                subject_length: emailData.subject.length,
                body_length: emailData.body.length,
                excessive_punctuation: hasExclamation ? 4 : 0,
                all_caps_words: [],
                suspicious_formatting: hasExclamation ? ['Excessive exclamation marks'] : [],
                explanation: 'Unusual formatting, excessive punctuation, or all-caps text can indicate phishing.'
              },
              language_quality: {
                suspicious_patterns: [],
                quality_score: 85,
                explanation: 'Poor grammar, unusual language patterns, or suspicious phrasing can indicate phishing.'
              }
            },
            recommendations: isPhishing ? [
              '🚨 DO NOT click on any links in this email',
              '🚨 DO NOT provide any personal information',
              '🚨 DO NOT download any attachments',
              '🚨 Delete this email immediately',
              '📧 Report this email as phishing to your email provider',
              '🔍 Verify any claims by contacting the organization directly through official channels'
            ] : [
              '✅ This email appears to be safe',
              '🔍 Always verify sender identity before taking any action',
              '🔗 Be cautious with any links, even in legitimate emails'
            ],
            red_flags: isPhishing ? [
              urgencyScore >= 2 ? 'Multiple urgency indicators detected' : null,
              threatScore > 0 ? 'Threats or pressure tactics used' : null,
              financialScore > 0 ? 'Unsolicited financial offers or prizes' : null,
              hasUrls ? 'Suspicious links present' : null,
              hasExclamation ? 'Excessive exclamation marks' : null
            ].filter(Boolean) : []
          }
        };
        
        saveAnalysisToHistory('email', demoResult);
        setLastAnalysisType('email');
        setShowCompletion(true);
        
        // Create report automatically (non-blocking)
        createReport(demoResult, 'email').catch(() => {
          // Silently handle report creation errors
        });
        
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
      const isUp = await healthCheck(800);
      if (!isUp) {
        throw new TypeError('Failed to fetch');
      }
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${getApiBase()}/analyze/media`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      saveAnalysisToHistory('deepfake', result);
      setCurrentDeepfakeResult(result);
      setLastAnalysisType('deepfake');
      setShowCompletion(true);
      
      // Create report automatically (non-blocking)
      createReport(result, result.file_type || 'image').catch(() => {
        // Silently handle report creation errors
      });
      
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
        const isAudio = file.type.startsWith('audio/');
        const fileSize = file.size;
        
        // More realistic demo based on file characteristics
        let demoResult;
        if (fileSize > 10 * 1024 * 1024) { // Large files more likely to be suspicious
          demoResult = {
            label: 'AI-Generated',
            confidence: Math.floor(Math.random() * 20) + 70, // 70-90% confidence
            trust_score: Math.floor(Math.random() * 20) + 70,
            reason_analysis: 'High confidence AI-generated detection. This large media file shows characteristics commonly associated with AI-generated content.',
            frames_analyzed: isVideo ? Math.floor(Math.random() * 20) + 10 : undefined,
            duration: isAudio ? Math.floor(Math.random() * 30) + 10 : undefined
          };
        } else {
          demoResult = {
            label: Math.random() > 0.6 ? 'AI-Generated' : 'Human-Created',
          confidence: Math.floor(Math.random() * 40) + 30, // 30-70% confidence
          trust_score: Math.floor(Math.random() * 40) + 30,
            reason_analysis: Math.random() > 0.6 
            ? 'Moderate confidence AI-generated detection. This media appears to be artificially generated using AI technology.'
            : 'This media appears to be created by humans without AI manipulation.',
            frames_analyzed: isVideo ? Math.floor(Math.random() * 20) + 10 : undefined,
            duration: isAudio ? Math.floor(Math.random() * 30) + 10 : undefined
        };
        }
        
        saveAnalysisToHistory('deepfake', demoResult);
        setCurrentDeepfakeResult(demoResult);
        setLastAnalysisType('deepfake');
        setShowCompletion(true);
        
        // Create report automatically (non-blocking)
        createReport(demoResult, isVideo ? 'video' : isAudio ? 'audio' : 'image').catch(() => {
          // Silently handle report creation errors
        });
        
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
    console.log('handleAnalyzeAnother called');
    setShowCompletion(false);
    setLastAnalysisType(null);
    toast({
      title: "Ready for new analysis",
      description: "You can now analyze another email or media file.",
    });
  };

  const handleClearForm = () => {
    console.log('handleClearForm called');
    setShowCompletion(false);
    setLastAnalysisType(null);
    setCurrentDeepfakeResult(null);
    toast({
      title: "Form cleared",
      description: "You can now start a new analysis.",
    });
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
            
            {/* Navigation and Stats */}
            <div className="flex items-center space-x-4">
              <Link to="/reports">
                <Button variant="outline" className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>View Reports</span>
                </Button>
              </Link>
              
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
          result={currentDeepfakeResult}
        />
          </TabsContent>
        </Tabs>

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