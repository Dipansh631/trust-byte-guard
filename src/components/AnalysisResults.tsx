import { ArrowLeft, Shield, AlertTriangle, CheckCircle, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export interface AnalysisResult {
  type: 'email' | 'deepfake';
  score: number; // 0-100, higher is more suspicious
  verdict: 'safe' | 'suspicious' | 'dangerous';
  summary: string;
  details: string[];
  recommendations?: string[];
}

interface AnalysisResultsProps {
  result: AnalysisResult;
  onBack: () => void;
  onNewAnalysis: () => void;
}

const AnalysisResults = ({ result, onBack, onNewAnalysis }: AnalysisResultsProps) => {
  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'safe':
        return {
          bg: 'bg-success/10',
          border: 'border-success/30',
          text: 'text-success',
          icon: CheckCircle,
        };
      case 'suspicious':
        return {
          bg: 'bg-warning/10',
          border: 'border-warning/30',
          text: 'text-warning',
          icon: AlertTriangle,
        };
      case 'dangerous':
        return {
          bg: 'bg-destructive/10',
          border: 'border-destructive/30',
          text: 'text-destructive',
          icon: AlertTriangle,
        };
      default:
        return {
          bg: 'bg-muted',
          border: 'border-border',
          text: 'text-foreground',
          icon: Info,
        };
    }
  };

  const verdictStyle = getVerdictColor(result.verdict);
  const VerdictIcon = verdictStyle.icon;

  return (
    <section className="min-h-screen py-20 px-4">
      <div className="container mx-auto max-w-4xl">
        <Button
          variant="ghost"
          onClick={onBack}
          className="mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Button>

        <div className="space-y-6">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary shadow-lg">
              <Shield className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-4xl font-bold">Analysis Complete</h1>
          </div>

          {/* Verdict Card */}
          <Card className={`p-8 ${verdictStyle.bg} border-2 ${verdictStyle.border}`}>
            <div className="flex flex-col items-center text-center space-y-4">
              <VerdictIcon className={`w-16 h-16 ${verdictStyle.text}`} />
              <div className="space-y-2">
                <h2 className={`text-3xl font-bold capitalize ${verdictStyle.text}`}>
                  {result.verdict}
                </h2>
                <p className="text-lg">{result.summary}</p>
              </div>
              
              {/* Confidence Score */}
              <div className="w-full max-w-md space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Suspicion Level</span>
                  <span className="font-medium">{result.score}%</span>
                </div>
                <Progress value={result.score} className="h-3" />
              </div>
            </div>
          </Card>

          {/* Details */}
          {result.details.length > 0 && (
            <Card className="p-6 space-y-4">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <Info className="w-5 h-5 text-primary" />
                What We Found
              </h3>
              <ul className="space-y-3">
                {result.details.map((detail, index) => (
                  <li key={index} className="flex gap-3 items-start">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span className="text-muted-foreground">{detail}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <Card className="p-6 space-y-4 bg-accent/5 border-accent/20">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <Shield className="w-5 h-5 text-accent" />
                Our Recommendations
              </h3>
              <ul className="space-y-3">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="flex gap-3 items-start">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                    <span className="text-muted-foreground">{rec}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <Button
              variant="hero"
              size="lg"
              onClick={onNewAnalysis}
              className="flex-1"
            >
              Analyze Another {result.type === 'email' ? 'Email' : 'Image'}
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={onBack}
              className="flex-1"
            >
              Return to Home
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AnalysisResults;