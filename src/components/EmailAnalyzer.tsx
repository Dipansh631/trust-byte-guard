import { useState } from "react";
import { Mail, Upload, Loader2, Shield, AlertTriangle, CheckCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "@/hooks/use-toast";
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface EmailAnalyzerProps {
  onAnalyze: (emailData: { subject: string; body: string }) => void;
  isAnalyzing: boolean;
  onClearForm?: () => void;
}

interface AnalysisResult {
  label: string;
  confidence: number;
  trust_score: number;
  suspicious_phrases: string[];
  reason_analysis: string;
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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
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
        <div className="grid md:grid-cols-2 gap-6">
          {/* Confidence Gauge */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {getLabelIcon(result.label)}
                <span>Analysis Result</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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
            </CardContent>
          </Card>

          {/* Detailed Analysis */}
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
        </div>
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