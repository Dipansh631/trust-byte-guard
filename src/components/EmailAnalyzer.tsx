import { useState } from "react";
import { Mail, Upload, Loader2, Shield, AlertTriangle, CheckCircle, X, Info, ExternalLink, AlertCircle, ChevronDown, FileText, Brain, Target, Zap, Users, DollarSign, Clock, AlertOctagon, Globe, Type, BookOpen, TrendingUp, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface EmailAnalyzerProps {
  onAnalyze: (emailData: { subject: string; body: string }) => void;
  isAnalyzing: boolean;
  onClearForm?: () => void;
}

interface DetailedAnalysis {
  overall_assessment: {
    label: string;
    confidence: number;
    risk_level: string;
    summary: string;
  };
  pattern_analysis: {
    urgency_indicators: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
    authority_claims: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
    financial_incentives: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
    action_requirements: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
    social_engineering: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
    threats_and_pressure: {
      score: number;
      patterns_found: string[];
      explanation: string;
    };
  };
  technical_analysis: {
    urls_and_links: {
      total_urls: number;
      suspicious_urls: string[];
      shortened_urls: string[];
      explanation: string;
    };
    email_structure: {
      subject_length: number;
      body_length: number;
      excessive_punctuation: number;
      all_caps_words: string[];
      suspicious_formatting: string[];
      explanation: string;
    };
    language_quality: {
      suspicious_patterns: string[];
      quality_score: number;
      explanation: string;
    };
  };
  recommendations: string[];
  red_flags: string[];
}

interface AnalysisResult {
  label: string;
  confidence: number;
  trust_score: number;
  suspicious_phrases: string[];
  reason_analysis: string;
  detailed_analysis?: DetailedAnalysis;
}

const EmailAnalyzer = ({ onAnalyze, isAnalyzing, onClearForm }: EmailAnalyzerProps) => {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = () => {
    if (!subject.trim() && !body.trim()) {
      toast({
        title: "Email content required",
        description: "Please enter at least a subject or body text to analyze.",
        variant: "destructive",
      });
      return;
    }
    onAnalyze({ subject, body });
  };

  const handleAnalyzeAnother = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('EmailAnalyzer: handleAnalyzeAnother called');
    setSubject("");
    setBody("");
    setResult(null);
    onClearForm?.();
    toast({
      title: "Ready for new analysis",
      description: "Please enter new email content to analyze.",
    });
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      // Try to parse email format
      const lines = content.split('\n');
      let emailSubject = '';
      let emailBody = '';
      let inBody = false;
      
      for (const line of lines) {
        if (line.toLowerCase().startsWith('subject:')) {
          emailSubject = line.substring(8).trim();
        } else if (line.trim() === '' && emailSubject) {
          inBody = true;
        } else if (inBody) {
          emailBody += line + '\n';
        }
      }
      
      setSubject(emailSubject);
      setBody(emailBody.trim());
      toast({
        title: "File loaded",
        description: "Email content has been parsed and loaded successfully.",
      });
    };
    reader.readAsText(file);
  };

  const highlightSuspiciousPhrases = (text: string, phrases: string[]) => {
    let highlightedText = text;
    phrases.forEach(phrase => {
      const regex = new RegExp(`(${phrase})`, 'gi');
      highlightedText = highlightedText.replace(regex, '<span class="bg-red-200 text-red-800 px-1 rounded font-semibold">$1</span>');
    });
    return highlightedText;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "#ef4444"; // red
    if (confidence >= 60) return "#f59e0b"; // amber
    if (confidence >= 40) return "#eab308"; // yellow
    return "#10b981"; // green
  };

  const getLabelIcon = (label: string) => {
    if (label === "Phishing") {
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getLabelColor = (label: string) => {
    if (label === "Phishing") return "destructive";
    return "default";
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "HIGH RISK": return "destructive";
      case "MEDIUM RISK": return "secondary";
      case "LOW RISK": return "outline";
      default: return "default";
    }
  };

  const renderPatternAnalysis = (pattern: any, title: string, icon: React.ReactNode) => {
    if (pattern.score === 0) return null;
    
    return (
      <Card className="border-l-4 border-l-red-500">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center space-x-2 text-sm">
            {icon}
            <span>{title}</span>
            <Badge variant="destructive" className="text-xs">
              Score: {pattern.score}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            <div className="flex flex-wrap gap-1">
              {pattern.patterns_found.map((phrase: string, index: number) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {phrase}
                </Badge>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              {pattern.explanation}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Input Card */}
      <Card className="p-6 space-y-4">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Mail className="w-5 h-5" />
            <span>Email Analysis</span>
          </CardTitle>
          <CardDescription>
            Enter the email subject and body content for AI-powered phishing detection
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Email Subject</label>
            <Input
              placeholder="Enter email subject..."
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              disabled={isAnalyzing}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Email Body</label>
            <Textarea
              placeholder="Enter email body content..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="min-h-[200px] resize-none"
              disabled={isAnalyzing}
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="file"
                accept=".txt,.eml,.msg"
                onChange={handleFileUpload}
                className="hidden"
                id="email-upload"
                disabled={isAnalyzing}
              />
              <label htmlFor="email-upload">
                <Button
                  variant="outline"
                  className="w-full"
                  asChild
                  disabled={isAnalyzing}
                >
                  <span>
                    <Upload className="w-4 h-4" />
                    Upload Email File
                  </span>
                </Button>
              </label>
            </div>

            <Button
              variant="default"
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!subject.trim() && !body.trim())}
              className="flex-1"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  Analyze Email
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Overall Assessment */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getLabelIcon(result.label)}
                  <span>Analysis Result</span>
                </div>
                {result.detailed_analysis && (
                  <Badge variant={getRiskLevelColor(result.detailed_analysis.overall_assessment.risk_level)}>
                    {result.detailed_analysis.overall_assessment.risk_level}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                {/* Confidence Gauge */}
                <div className="flex justify-center">
                  <div className="w-32 h-32">
                    <CircularProgressbar
                      value={result.confidence}
                      text={`${result.confidence}%`}
                      styles={buildStyles({
                        pathColor: getConfidenceColor(result.confidence),
                        textColor: getConfidenceColor(result.confidence),
                        trailColor: '#e5e7eb',
                        textSize: '16px',
                      })}
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="text-center space-y-2">
                    <Badge variant={getLabelColor(result.label)} className="text-lg px-3 py-1">
                      {result.label}
                    </Badge>
                    <p className="text-sm text-muted-foreground">
                      Confidence: {result.confidence}%
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Trust Score: {result.trust_score}%
                    </p>
                  </div>
                  
                  {result.detailed_analysis && (
                    <div>
                      <h4 className="font-medium mb-2">Summary</h4>
                      <p className="text-sm text-muted-foreground">
                        {result.detailed_analysis.overall_assessment.summary}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Analysis */}
          {result.detailed_analysis && (
            <div className="space-y-4">
              {/* Pattern Analysis */}
              <Collapsible>
                <CollapsibleTrigger asChild>
                  <Button variant="outline" className="w-full justify-between">
                    <span className="flex items-center space-x-2">
                      <AlertCircle className="w-4 h-4" />
                      <span>Pattern Analysis</span>
                    </span>
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-4 mt-4">
                  <div className="grid gap-4">
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.urgency_indicators,
                      "Urgency Indicators",
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                    )}
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.authority_claims,
                      "Authority Claims",
                      <Shield className="w-4 h-4 text-blue-500" />
                    )}
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.financial_incentives,
                      "Financial Incentives",
                      <ExternalLink className="w-4 h-4 text-green-500" />
                    )}
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.action_requirements,
                      "Action Requirements",
                      <Info className="w-4 h-4 text-yellow-500" />
                    )}
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.social_engineering,
                      "Social Engineering",
                      <Mail className="w-4 h-4 text-purple-500" />
                    )}
                    {renderPatternAnalysis(
                      result.detailed_analysis.pattern_analysis.threats_and_pressure,
                      "Threats & Pressure",
                      <X className="w-4 h-4 text-red-600" />
                    )}
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Technical Analysis */}
              <Collapsible>
                <CollapsibleTrigger asChild>
                  <Button variant="outline" className="w-full justify-between">
                    <span className="flex items-center space-x-2">
                      <Info className="w-4 h-4" />
                      <span>Technical Analysis</span>
                    </span>
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-4 mt-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* URLs and Links */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">URLs & Links</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Total URLs:</span>
                          <Badge variant="outline">{result.detailed_analysis.technical_analysis.urls_and_links.total_urls}</Badge>
                        </div>
                        {result.detailed_analysis.technical_analysis.urls_and_links.suspicious_urls.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-red-600">Suspicious URLs:</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {result.detailed_analysis.technical_analysis.urls_and_links.suspicious_urls.map((url, index) => (
                                <Badge key={index} variant="destructive" className="text-xs">
                                  {url.length > 30 ? url.substring(0, 30) + "..." : url}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        <p className="text-xs text-muted-foreground">
                          {result.detailed_analysis.technical_analysis.urls_and_links.explanation}
                        </p>
                      </CardContent>
                    </Card>

                    {/* Email Structure */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">Email Structure</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Subject Length:</span>
                          <span>{result.detailed_analysis.technical_analysis.email_structure.subject_length} chars</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Body Length:</span>
                          <span>{result.detailed_analysis.technical_analysis.email_structure.body_length} chars</span>
                        </div>
                        {result.detailed_analysis.technical_analysis.email_structure.excessive_punctuation > 0 && (
                          <div className="flex justify-between text-sm">
                            <span>Exclamation Marks:</span>
                            <Badge variant="destructive">{result.detailed_analysis.technical_analysis.email_structure.excessive_punctuation}</Badge>
                          </div>
                        )}
                        {result.detailed_analysis.technical_analysis.email_structure.suspicious_formatting.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-red-600">Suspicious Formatting:</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {result.detailed_analysis.technical_analysis.email_structure.suspicious_formatting.map((format, index) => (
                                <Badge key={index} variant="destructive" className="text-xs">
                                  {format}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        <p className="text-xs text-muted-foreground">
                          {result.detailed_analysis.technical_analysis.email_structure.explanation}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </CollapsibleContent>
              </Collapsible>

              {/* Red Flags */}
              {result.detailed_analysis.red_flags.length > 0 && (
                <Card className="border-red-200 bg-red-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-red-700">
                      <AlertTriangle className="w-5 h-5" />
                      <span>Red Flags</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {result.detailed_analysis.red_flags.map((flag, index) => (
                        <div key={index} className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-red-700">{flag}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span>Security Recommendations</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {result.detailed_analysis.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-green-700">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Basic Analysis (fallback) */}
          {!result.detailed_analysis && (
            <Card>
              <CardHeader>
                <CardTitle>Detailed Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Reason Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    {result.reason_analysis}
                  </p>
                </div>

                {result.suspicious_phrases.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Suspicious Phrases Detected</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.suspicious_phrases.map((phrase, index) => (
                        <Badge key={index} variant="destructive" className="text-xs">
                          {phrase}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-medium mb-2">Trust Score</h4>
                  <Progress value={result.trust_score} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {result.trust_score}% trust level
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Detailed Analysis Report Section */}
      {result && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-blue-700">
              <FileText className="w-5 h-5" />
              <span>Detailed Email Analysis Report</span>
            </CardTitle>
            <CardDescription className="text-blue-600">
              Comprehensive analysis explaining why this email is classified as {result.label.toLowerCase()}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Analysis Theory Section */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-800">Analysis Theory & Methodology</h3>
              </div>
              
              <div className="grid md:grid-cols-2 gap-4">
                <Card className="bg-white">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center space-x-2">
                      <Target className="w-4 h-4 text-orange-500" />
                      <span>Pattern Recognition</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-xs text-gray-600">
                      Our AI analyzes email content using advanced pattern recognition to identify common phishing techniques:
                    </p>
                    <ul className="text-xs text-gray-600 space-y-1 ml-4">
                      <li>• <strong>Urgency Tactics:</strong> Creating false time pressure</li>
                      <li>• <strong>Authority Claims:</strong> Impersonating trusted entities</li>
                      <li>• <strong>Social Engineering:</strong> Manipulating human psychology</li>
                      <li>• <strong>Financial Incentives:</strong> Promising rewards or threatening losses</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center space-x-2">
                      <BarChart3 className="w-4 h-4 text-green-500" />
                      <span>Technical Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-xs text-gray-600">
                      Technical indicators help identify suspicious email characteristics:
                    </p>
                    <ul className="text-xs text-gray-600 space-y-1 ml-4">
                      <li>• <strong>URL Analysis:</strong> Checking for suspicious domains and redirects</li>
                      <li>• <strong>Language Quality:</strong> Detecting poor grammar and spelling</li>
                      <li>• <strong>Email Structure:</strong> Analyzing formatting and composition</li>
                      <li>• <strong>Metadata:</strong> Examining sender information and headers</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>

            <Separator className="bg-blue-200" />

            {/* Detailed Classification Explanation */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-800">Classification Explanation</h3>
              </div>

              <Card className={`${result.label === 'Phishing' ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}`}>
                <CardContent className="pt-4">
                  <div className="flex items-start space-x-3">
                    {result.label === 'Phishing' ? (
                      <AlertTriangle className="w-6 h-6 text-red-500 mt-1" />
                    ) : (
                      <CheckCircle className="w-6 h-6 text-green-500 mt-1" />
                    )}
                    <div className="space-y-3">
                      <div>
                        <h4 className={`font-semibold ${result.label === 'Phishing' ? 'text-red-800' : 'text-green-800'}`}>
                          Why this email is classified as "{result.label}"
                        </h4>
                        <p className={`text-sm mt-1 ${result.label === 'Phishing' ? 'text-red-700' : 'text-green-700'}`}>
                          {result.reason_analysis}
                        </p>
                      </div>

                      {result.detailed_analysis && (
                        <div className="space-y-3">
                          <div className="grid md:grid-cols-3 gap-3">
                            <div className="text-center">
                              <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-2 ${result.label === 'Phishing' ? 'bg-red-100' : 'bg-green-100'}`}>
                                <span className={`text-lg font-bold ${result.label === 'Phishing' ? 'text-red-600' : 'text-green-600'}`}>
                                  {result.confidence}%
                                </span>
                              </div>
                              <p className={`text-xs font-medium ${result.label === 'Phishing' ? 'text-red-700' : 'text-green-700'}`}>
                                Confidence Level
                              </p>
                            </div>
                            <div className="text-center">
                              <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-2 ${result.detailed_analysis.overall_assessment.risk_level === 'High' ? 'bg-red-100' : result.detailed_analysis.overall_assessment.risk_level === 'Medium' ? 'bg-yellow-100' : 'bg-green-100'}`}>
                                <Shield className={`w-6 h-6 ${result.detailed_analysis.overall_assessment.risk_level === 'High' ? 'text-red-600' : result.detailed_analysis.overall_assessment.risk_level === 'Medium' ? 'text-yellow-600' : 'text-green-600'}`} />
                              </div>
                              <p className={`text-xs font-medium ${result.detailed_analysis.overall_assessment.risk_level === 'High' ? 'text-red-700' : result.detailed_analysis.overall_assessment.risk_level === 'Medium' ? 'text-yellow-700' : 'text-green-700'}`}>
                                Risk Level: {result.detailed_analysis.overall_assessment.risk_level}
                              </p>
                            </div>
                            <div className="text-center">
                              <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-2 bg-blue-100">
                                <span className="text-lg font-bold text-blue-600">
                                  {result.detailed_analysis.red_flags.length}
                                </span>
                              </div>
                              <p className="text-xs font-medium text-blue-700">
                                Red Flags Detected
                              </p>
                            </div>
                          </div>

                          <div className="mt-4">
                            <h5 className="font-medium text-gray-800 mb-2">Analysis Summary:</h5>
                            <p className="text-sm text-gray-600 bg-white p-3 rounded-lg border">
                              {result.detailed_analysis.overall_assessment.summary}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Separator className="bg-blue-200" />

            {/* Detailed Breakdown */}
            {result.detailed_analysis && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-semibold text-blue-800">Detailed Analysis Breakdown</h3>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  {/* Pattern Analysis Summary */}
                  <Card className="bg-white">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-purple-500" />
                        <span>Pattern Analysis Summary</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {Object.entries(result.detailed_analysis.pattern_analysis).map(([key, analysis]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-xs text-gray-600 capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <div className="flex items-center space-x-2">
                            <Progress 
                              value={analysis.score} 
                              className="w-16 h-2" 
                            />
                            <span className={`text-xs font-medium ${analysis.score > 50 ? 'text-red-600' : 'text-green-600'}`}>
                              {analysis.score}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Technical Analysis Summary */}
                  <Card className="bg-white">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center space-x-2">
                        <Globe className="w-4 h-4 text-blue-500" />
                        <span>Technical Analysis Summary</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">URLs Found:</span>
                        <Badge variant="outline">
                          {result.detailed_analysis.technical_analysis.urls_and_links.total_urls}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Suspicious URLs:</span>
                        <Badge variant={result.detailed_analysis.technical_analysis.urls_and_links.suspicious_urls.length > 0 ? "destructive" : "secondary"}>
                          {result.detailed_analysis.technical_analysis.urls_and_links.suspicious_urls.length}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Language Quality:</span>
                        <Badge variant={result.detailed_analysis.technical_analysis.language_quality.quality_score < 70 ? "destructive" : "secondary"}>
                          {result.detailed_analysis.technical_analysis.language_quality.quality_score}%
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Excessive Punctuation:</span>
                        <Badge variant={result.detailed_analysis.technical_analysis.email_structure.excessive_punctuation > 3 ? "destructive" : "secondary"}>
                          {result.detailed_analysis.technical_analysis.email_structure.excessive_punctuation}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            <Separator className="bg-blue-200" />

            {/* Security Recommendations */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-800">Security Recommendations</h3>
              </div>

              {result.detailed_analysis ? (
                <div className="grid md:grid-cols-2 gap-4">
                  <Card className="bg-white">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-green-700">Immediate Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {result.detailed_analysis.recommendations.slice(0, 3).map((rec, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-xs text-gray-700">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-blue-700">Best Practices</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex items-start space-x-2">
                          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-xs text-gray-700">Always verify sender identity through official channels</span>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-xs text-gray-700">Never click suspicious links or download attachments</span>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-xs text-gray-700">Report suspicious emails to your IT security team</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="bg-white">
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700">Verify the sender's identity through official channels</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700">Never click on suspicious links or download unexpected attachments</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700">Report suspicious emails to your IT security team immediately</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Highlighted Text Preview */}
      {result && result.suspicious_phrases.length > 0 && (subject || body) && (
        <Card>
          <CardHeader>
            <CardTitle>Text with Highlighted Suspicious Phrases</CardTitle>
            <CardDescription>
              Red highlights indicate potentially suspicious phrases
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {subject && (
                <div>
                  <h4 className="font-medium mb-2">Subject:</h4>
                  <div 
                    className="p-3 bg-muted rounded-lg text-sm"
                    dangerouslySetInnerHTML={{ 
                      __html: highlightSuspiciousPhrases(subject, result.suspicious_phrases) 
                    }}
                  />
                </div>
              )}
              {body && (
                <div>
                  <h4 className="font-medium mb-2">Body:</h4>
                  <div 
                    className="p-3 bg-muted rounded-lg text-sm max-h-40 overflow-y-auto"
                    dangerouslySetInnerHTML={{ 
                      __html: highlightSuspiciousPhrases(body, result.suspicious_phrases) 
                    }}
                  />
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analyze Another Button */}
      {result && (
        <Card className="p-4 bg-green-50 border-green-200">
          <div className="text-center space-y-3">
            <div className="flex items-center justify-center space-x-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">Analysis Complete!</span>
            </div>
            <p className="text-sm text-green-600">
              Would you like to analyze another email?
            </p>
            <Button
              onClick={(e) => handleAnalyzeAnother(e)}
              variant="outline"
              className="border-green-300 text-green-700 hover:bg-green-100"
              type="button"
            >
              <Mail className="w-4 h-4 mr-2" />
              Analyze Another Email
            </Button>
          </div>
        </Card>
      )}

      {/* Tips */}
      <Card className="p-4 bg-primary/5 border-primary/20">
        <h3 className="font-semibold mb-2 flex items-center gap-2">
          <Mail className="w-4 h-4 text-primary" />
          Tips for best results
        </h3>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• Include the complete email subject and body</li>
          <li>• Don't modify the original content</li>
          <li>• Include any suspicious links or attachments mentioned</li>
          <li>• The AI analyzes patterns, language, and context</li>
        </ul>
      </Card>
    </div>
  );
};

export default EmailAnalyzer;