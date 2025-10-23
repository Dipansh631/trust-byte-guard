import { CheckCircle, Mail, Image, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface AnalysisCompleteProps {
  type: 'email' | 'deepfake';
  onAnalyzeAnother: () => void;
  onClearForm: () => void;
}

const AnalysisComplete = ({ type, onAnalyzeAnother, onClearForm }: AnalysisCompleteProps) => {
  const isEmail = type === 'email';
  
  return (
    <Card className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
      <CardContent className="p-0">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2 text-green-700">
            <CheckCircle className="w-6 h-6" />
            <span className="text-lg font-semibold">Analysis Complete!</span>
          </div>
          
          <p className="text-sm text-green-600 max-w-md mx-auto">
            {isEmail 
              ? "Your email has been analyzed for phishing threats. Would you like to analyze another email?"
              : "Your media file has been analyzed for deepfake detection. Would you like to analyze another file?"
            }
          </p>
          
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={onAnalyzeAnother}
              variant="default"
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              {isEmail ? (
                <>
                  <Mail className="w-4 h-4 mr-2" />
                  Analyze Another Email
                </>
              ) : (
                <>
                  <Image className="w-4 h-4 mr-2" />
                  Analyze Another File
                </>
              )}
            </Button>
            
            <Button
              onClick={onClearForm}
              variant="outline"
              className="border-green-300 text-green-700 hover:bg-green-100"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Clear Form
            </Button>
          </div>
          
          <div className="text-xs text-green-500 mt-2">
            💡 Tip: You can also switch between Email and Deepfake tabs to try different analysis types
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisComplete;
