import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import UploadSection from "@/components/UploadSection";
import UploadedFiles from "@/components/UploadedFiles";
import ChatInterface from "@/components/ChatInterface";
import DataPreview from "@/components/DataPreview";
import { sessionService } from "@/services/sessionService";
import { useApi } from "@/hooks/useApi";
import { Upload, MessageSquare, BarChart3, FileText } from "lucide-react";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: string;
}

const Index = () => {
  const [activeTab, setActiveTab] = useState("upload");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  // Get current session and files
  const { data: session, refetch: refetchSession } = useApi(() => sessionService.getCurrentSession());

  // Update uploaded files when session data changes
  useEffect(() => {
    if (session?.files) {
      const files: UploadedFile[] = session.files.map(file => ({
        id: file.fileId,
        name: file.filename,
        size: file.size,
        uploadedAt: file.uploadedAt
      }));
      setUploadedFiles(files);
      
      // Auto-switch to chat tab if files are uploaded
      if (files.length > 0 && activeTab === "upload") {
        setActiveTab("chat");
      }
      
      // Auto-select first file for preview
      if (files.length > 0 && !selectedFileId) {
        setSelectedFileId(files[0].id);
      }
    }
  }, [session, activeTab, selectedFileId]);

  const handleFileUpload = () => {
    // Refresh session data after file upload
    refetchSession();
  };

  const selectedFile = uploadedFiles.find(f => f.id === selectedFileId);

  return (
    <div className="min-h-screen bg-background">
      <main>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Navigation Tabs */}
          <div className="border-b">
            <div className="max-w-6xl mx-auto px-4">
              <TabsList className="grid w-full grid-cols-4 max-w-2xl">
                <TabsTrigger value="upload" className="flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Upload
                </TabsTrigger>
                <TabsTrigger value="chat" className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Chat
                </TabsTrigger>
                <TabsTrigger value="preview" className="flex items-center gap-2" disabled={uploadedFiles.length === 0}>
                  <BarChart3 className="w-4 h-4" />
                  Preview
                </TabsTrigger>
                <TabsTrigger value="files" className="flex items-center gap-2" disabled={uploadedFiles.length === 0}>
                  <FileText className="w-4 h-4" />
                  Files
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          {/* Upload Tab */}
          <TabsContent value="upload" className="mt-0">
            <UploadSection />
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="mt-0">
            <ChatInterface 
              uploadedFiles={uploadedFiles.map(f => ({ id: f.id, name: f.name }))}
            />
          </TabsContent>

          {/* Data Preview Tab */}
          <TabsContent value="preview" className="mt-0">
            <div className="max-w-7xl mx-auto px-4 py-8">
              {uploadedFiles.length === 0 ? (
                <div className="text-center py-12">
                  <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Data to Preview</h3>
                  <p className="text-muted-foreground">
                    Upload files to see data preview and visualizations.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* File Selector */}
                  {uploadedFiles.length > 1 && (
                    <div className="flex items-center gap-4">
                      <span className="text-sm font-medium">Select file to preview:</span>
                      <div className="flex flex-wrap gap-2">
                        {uploadedFiles.map((file) => (
                          <button
                            key={file.id}
                            onClick={() => setSelectedFileId(file.id)}
                            className={`px-3 py-1 rounded-md text-sm transition-colors ${
                              selectedFileId === file.id
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary hover:bg-secondary/80'
                            }`}
                          >
                            {file.name}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Data Preview Component */}
                  {selectedFileId && selectedFile && (
                    <DataPreview 
                      fileId={selectedFileId}
                      fileName={selectedFile.name}
                    />
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Files Tab */}
          <TabsContent value="files" className="mt-0">
            <div className="max-w-4xl mx-auto px-4 py-8">
              <UploadedFiles />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
