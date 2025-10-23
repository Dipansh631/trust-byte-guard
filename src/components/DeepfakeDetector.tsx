import { useState } from "react";
import { Image as ImageIcon, Upload, Loader2, X, AlertTriangle, CheckCircle, Video } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "@/hooks/use-toast";
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface DeepfakeDetectorProps {
  onAnalyze: (file: File) => void;
  isAnalyzing: boolean;
  onClearForm?: () => void;
  result?: AnalysisResult | null;
}

interface AnalysisResult {
  label: string;
  confidence: number;
  trust_score: number;
  reason_analysis: string;
  frames_analyzed?: number;
}

const DeepfakeDetector = ({ onAnalyze, isAnalyzing, onClearForm, result: propResult }: DeepfakeDetectorProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  // Use prop result if available, otherwise use local state
  const displayResult = propResult || result;

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      toast({
        title: "Invalid file type",
        description: "Please select an image or video file (JPG, PNG, MP4, etc.)",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (max 50MB for videos, 20MB for images)
    const maxSize = file.type.startsWith('video/') ? 50 * 1024 * 1024 : 20 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: `Please select a file smaller than ${file.type.startsWith('video/') ? '50MB' : '20MB'}.`,
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
    setResult(null); // Clear previous results
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    toast({
      title: "Media uploaded successfully",
      description: "Now ready for analysis",
    });
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
  };

  const handleAnalyze = () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please select a file to analyze.",
        variant: "destructive",
      });
      return;
    }
    onAnalyze(selectedFile);
  };

  const handleAnalyzeAnother = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('DeepfakeDetector: handleAnalyzeAnother called');
    
    // Clear current state
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    
    // Trigger file input dialog
    const fileInput = document.getElementById('media-upload') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
    
    onClearForm?.();
  };

  const handleClearForm = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('DeepfakeDetector: handleClearForm called');
    
    // Clear all state
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    
    onClearForm?.();
    
    toast({
      title: "Form cleared",
      description: "Upload area is ready for a new file.",
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "#ef4444"; // red
    if (confidence >= 60) return "#f59e0b"; // amber
    if (confidence >= 40) return "#eab308"; // yellow
    return "#10b981"; // green
  };

  const getLabelIcon = (label: string) => {
    if (label === "AI-Generated") {
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getLabelColor = (label: string) => {
    if (label === "AI-Generated") return "destructive";
    return "default";
  };

  const isVideo = selectedFile?.type.startsWith('video/');

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Upload Card */}
      <Card className="p-6 space-y-4">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {isVideo ? <Video className="w-5 h-5" /> : <ImageIcon className="w-5 h-5" />}
            <span>Media Upload</span>
          </CardTitle>
          <CardDescription>
            Upload an image or video to analyze for deepfake detection
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {previewUrl ? (
            <div className="space-y-4">
              <div className="relative rounded-lg overflow-hidden border border-border bg-muted">
                {isVideo ? (
                  <video
                    src={previewUrl}
                    controls
                    className="w-full h-auto max-h-[400px] object-contain"
                  />
                ) : (
                  <img
                    src={previewUrl}
                    alt="Selected for analysis"
                    className="w-full h-auto max-h-[400px] object-contain"
                  />
                )}
                {!isAnalyzing && (
                  <button
                    onClick={handleRemoveFile}
                    className="absolute top-2 right-2 p-2 rounded-full bg-background/80 hover:bg-background transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              <div className="text-sm text-muted-foreground">
                <span className="font-medium">File:</span> {selectedFile?.name}
                <span className="ml-2 text-xs">
                  ({isVideo ? 'Video' : 'Image'} • {((selectedFile?.size || 0) / (1024 * 1024)).toFixed(1)}MB)
                </span>
              </div>
            </div>
          ) : (
            <div className="border-2 border-dashed border-border rounded-lg p-12 text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full bg-muted flex items-center justify-center">
                <Upload className="w-8 h-8 text-muted-foreground" />
              </div>
              <div className="space-y-2">
                <p className="text-lg font-medium">Drop media here</p>
                <p className="text-sm text-muted-foreground">or click to browse images and videos</p>
              </div>
              <input
                type="file"
                accept="image/*,video/*"
                onChange={handleFileSelect}
                className="hidden"
                id="media-upload"
                disabled={isAnalyzing}
              />
              <label htmlFor="media-upload">
                <Button variant="outline" asChild disabled={isAnalyzing}>
                  <span>
                    <Upload className="w-4 h-4" />
                    Select Media
                  </span>
                </Button>
              </label>
            </div>
          )}

          {selectedFile && (
            <Button
              variant="default"
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing {isVideo ? 'Video' : 'Image'}...
                </>
              ) : (
                <>
                  <ImageIcon className="w-4 h-4" />
                  Analyze for Deepfakes
                </>
              )}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Results Display */}
      {displayResult && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Confidence Gauge */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {getLabelIcon(displayResult.label)}
                <span>Analysis Result</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-center">
                <div className="w-32 h-32">
                  <CircularProgressbar
                    value={displayResult.confidence}
                    text={`${displayResult.confidence}%`}
                    styles={buildStyles({
                      pathColor: getConfidenceColor(displayResult.confidence),
                      textColor: getConfidenceColor(displayResult.confidence),
                      trailColor: '#e5e7eb',
                      textSize: '16px',
                    })}
                  />
                </div>
              </div>
              
              <div className="text-center space-y-2">
                <Badge variant={getLabelColor(displayResult.label)} className="text-lg px-3 py-1">
                  {displayResult.label}
                </Badge>
                
                {/* AI Generation Status */}
                <div className="mt-3 p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center justify-center space-x-2">
                    {displayResult.label === "AI-Generated" ? (
                      <>
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        <span className="font-semibold text-red-700">AI-Generated Content Detected</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <span className="font-semibold text-green-700">Human-Created Content</span>
                      </>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {displayResult.label === "AI-Generated" 
                      ? "This media was created using artificial intelligence"
                      : "This media was created by humans without AI assistance"
                    }
                  </p>
                </div>
                
                <p className="text-sm text-muted-foreground">
                  Confidence: {displayResult.confidence}%
                </p>
                <p className="text-sm text-muted-foreground">
                  Trust Score: {displayResult.trust_score}%
                </p>
                {displayResult.frames_analyzed && (
                  <p className="text-xs text-muted-foreground">
                    Frames Analyzed: {displayResult.frames_analyzed}
                  </p>
                )}
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
                  {displayResult.reason_analysis}
                </p>
              </div>

              <div>
                <h4 className="font-medium mb-2">Trust Score</h4>
                <Progress value={displayResult.trust_score} className="h-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {displayResult.trust_score}% trust level
                </p>
              </div>

              {displayResult.frames_analyzed && (
                <div>
                  <h4 className="font-medium mb-2">Video Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    Analyzed {displayResult.frames_analyzed} frames from the video for consistency and authenticity.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analyze Another Button */}
      {displayResult && (
        <Card className="p-4 bg-green-50 border-green-200">
          <div className="text-center space-y-3">
            <div className="flex items-center justify-center space-x-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">Analysis Complete!</span>
            </div>
            <p className="text-sm text-green-600">
              Would you like to analyze another media file?
            </p>
            <div className="flex gap-2 justify-center">
              <Button
                onClick={handleAnalyzeAnother}
                variant="outline"
                className="border-green-300 text-green-700 hover:bg-green-100"
                type="button"
              >
                <ImageIcon className="w-4 h-4 mr-2" />
                Analyze Another File
              </Button>
              <Button
                onClick={handleClearForm}
                variant="outline"
                className="border-blue-300 text-blue-700 hover:bg-blue-100"
                type="button"
              >
                <X className="w-4 h-4 mr-2" />
                Clear Form
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Tips */}
      <Card className="p-4 bg-secondary/5 border-secondary/20">
        <h3 className="font-semibold mb-2 flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-secondary" />
          Tips for best results
        </h3>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• Use high-resolution images and videos when possible</li>
          <li>• Clear, well-lit content works best</li>
          <li>• Images/videos with faces show more detailed analysis</li>
          <li>• Maximum file size: 20MB for images, 50MB for videos</li>
          <li>• Supported formats: JPG, PNG, MP4, AVI, MOV</li>
        </ul>
      </Card>
    </div>
  );
};

export default DeepfakeDetector;