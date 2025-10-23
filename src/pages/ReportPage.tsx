import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  PieChart, Pie, Cell
} from "recharts";
import { 
  Mail, Image, Video, Volume2, FileText, AlertTriangle, CheckCircle, 
  TrendingUp, Shield, Eye, Download, Calendar, Clock
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface AnalysisReport {
  id: string;
  timestamp: string;
  type: 'email' | 'image' | 'video' | 'audio';
  analysis_data: {
    result: string;
    confidence: number;
    reasons: any;
    score_breakdown: any;
    label: string;
    trust_score: number;
    reason_analysis: string;
  };
  user_notes: string;
}

const ReportPage = () => {
  const [reports, setReports] = useState<AnalysisReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [userNotes, setUserNotes] = useState("");
  const [activeTab, setActiveTab] = useState("email");

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/reports');
      if (response.ok) {
        const data = await response.json();
        setReports(data.reports || []);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      toast({
        title: "Failed to load reports",
        description: "Could not connect to the backend server.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createReport = async (analysisData: any, type: string) => {
    try {
      const response = await fetch('http://localhost:8000/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          analysis_data: analysisData,
          user_notes: userNotes
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Report Created",
          description: "Analysis report has been saved successfully.",
        });
        fetchReports(); // Refresh the reports list
        setUserNotes("");
      }
    } catch (error) {
      console.error('Failed to create report:', error);
      toast({
        title: "Failed to create report",
        description: "Could not save the analysis report.",
        variant: "destructive",
      });
    }
  };

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'image': return <Image className="w-4 h-4" />;
      case 'video': return <Video className="w-4 h-4" />;
      case 'audio': return <Volume2 className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getResultColor = (result: string) => {
    if (result === 'phishing' || result === 'deepfake' || result === 'AI-Generated') return 'destructive';
    return 'default';
  };

  const getResultIcon = (result: string) => {
    if (result === 'phishing' || result === 'deepfake' || result === 'AI-Generated') {
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    }
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getChartData = (scoreBreakdown: any) => {
    return Object.entries(scoreBreakdown)
      .filter(([key]) => key !== 'overall_confidence')
      .map(([key, value]) => ({
        name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        score: value,
        fill: '#8884d8'
      }));
  };

  const getRadarData = (scoreBreakdown: any) => {
    return Object.entries(scoreBreakdown)
      .filter(([key]) => key !== 'overall_confidence')
      .map(([key, value]) => ({
        subject: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        A: value,
        fullMark: 100
      }));
  };

  const getPieData = (scoreBreakdown: any) => {
    const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
    return Object.entries(scoreBreakdown)
      .filter(([key]) => key !== 'overall_confidence')
      .map(([key, value], index) => ({
        name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: value,
        fill: colors[index % colors.length]
      }));
  };

  const filteredReports = reports.filter(report => {
    if (activeTab === 'email') return report.type === 'email';
    if (activeTab === 'image') return report.type === 'image';
    if (activeTab === 'video') return report.type === 'video';
    if (activeTab === 'audio') return report.type === 'audio';
    return true;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">AI Analysis Reports</h1>
                <p className="text-muted-foreground">
                  Detailed visual explanations of security analysis results
                </p>
              </div>
            </div>
            <Badge variant="outline" className="text-sm">
              {reports.length} Reports
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="email" className="flex items-center space-x-2">
              <Mail className="w-4 h-4" />
              <span>Email</span>
            </TabsTrigger>
            <TabsTrigger value="image" className="flex items-center space-x-2">
              <Image className="w-4 h-4" />
              <span>Image</span>
            </TabsTrigger>
            <TabsTrigger value="video" className="flex items-center space-x-2">
              <Video className="w-4 h-4" />
              <span>Video</span>
            </TabsTrigger>
            <TabsTrigger value="audio" className="flex items-center space-x-2">
              <Volume2 className="w-4 h-4" />
              <span>Audio</span>
            </TabsTrigger>
          </TabsList>

          {['email', 'image', 'video', 'audio'].map((tab) => (
            <TabsContent key={tab} value={tab} className="space-y-6">
              {/* Reports List */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    {getReportIcon(tab)}
                    <span>{tab.charAt(0).toUpperCase() + tab.slice(1)} Analysis Reports</span>
                  </CardTitle>
                  <CardDescription>
                    View detailed analysis reports for {tab} content
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                      <p className="text-muted-foreground mt-2">Loading reports...</p>
                    </div>
                  ) : filteredReports.length === 0 ? (
                    <div className="text-center py-8">
                      <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">No {tab} reports found</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Run some {tab} analysis to generate reports
                      </p>
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {filteredReports.map((report) => (
                        <Card 
                          key={report.id} 
                          className={`cursor-pointer transition-colors hover:bg-muted/50 ${
                            selectedReport?.id === report.id ? 'ring-2 ring-primary' : ''
                          }`}
                          onClick={() => setSelectedReport(report)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                {getResultIcon(report.analysis_data.result)}
                                <div>
                                  <div className="flex items-center space-x-2">
                                    <Badge variant={getResultColor(report.analysis_data.result)}>
                                      {report.analysis_data.label}
                                    </Badge>
                                    <span className="text-sm text-muted-foreground">
                                      {report.analysis_data.confidence}% confidence
                                    </span>
                                  </div>
                                  <p className="text-sm text-muted-foreground mt-1">
                                    {formatTimestamp(report.timestamp)}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                                <Calendar className="w-4 h-4" />
                                <span>{formatTimestamp(report.timestamp)}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Selected Report Details */}
              {selectedReport && selectedReport.type === tab && (
                <div className="grid lg:grid-cols-2 gap-6">
                  {/* Analysis Overview */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Shield className="w-5 h-5" />
                        <span>Analysis Overview</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Result:</span>
                        <Badge variant={getResultColor(selectedReport.analysis_data.result)}>
                          {selectedReport.analysis_data.label}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Confidence:</span>
                        <span className="text-lg font-semibold">
                          {selectedReport.analysis_data.confidence}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Trust Score:</span>
                        <span className="text-lg font-semibold text-green-600">
                          {selectedReport.analysis_data.trust_score}%
                        </span>
                      </div>
                      <div>
                        <span className="font-medium">Analysis Summary:</span>
                        <p className="text-sm text-muted-foreground mt-1">
                          {selectedReport.analysis_data.reason_analysis}
                        </p>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Score Breakdown Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <TrendingUp className="w-5 h-5" />
                        <span>Score Breakdown</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={getChartData(selectedReport.analysis_data.score_breakdown)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="score" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Detailed Reasons */}
                  <Card className="lg:col-span-2">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Eye className="w-5 h-5" />
                        <span>Detailed Analysis Reasons</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(selectedReport.analysis_data.reasons).map(([key, reason]: [string, any]) => (
                          <Card key={key} className="p-4">
                            <CardHeader className="p-0 pb-2">
                              <CardTitle className="text-sm font-medium">
                                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="p-0">
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-xs text-muted-foreground">Score:</span>
                                  <span className="text-sm font-semibold">{reason.score}%</span>
                                </div>
                                {reason.details && (
                                  <div>
                                    <span className="text-xs text-muted-foreground">Details:</span>
                                    <ul className="text-xs text-muted-foreground mt-1 space-y-1">
                                      {reason.details.map((detail: string, index: number) => (
                                        <li key={index}>• {detail}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                {reason.anomalies && reason.anomalies.length > 0 && (
                                  <div>
                                    <span className="text-xs text-red-600">Anomalies:</span>
                                    <ul className="text-xs text-red-600 mt-1 space-y-1">
                                      {reason.anomalies.map((anomaly: string, index: number) => (
                                        <li key={index}>• {anomaly}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* User Notes */}
                  {selectedReport.user_notes && (
                    <Card className="lg:col-span-2">
                      <CardHeader>
                        <CardTitle>User Notes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">
                          {selectedReport.user_notes}
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  );
};

export default ReportPage;
