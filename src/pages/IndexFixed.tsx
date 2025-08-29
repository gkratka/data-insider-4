import { useState, useCallback, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, MessageSquare, BarChart3, FileText } from "lucide-react";
import FileUpload, { UploadedFile } from "@/components/FileUpload";
import FilesTab from "@/components/FilesTab";
import { fileUploadService } from "@/services/fileUploadService";

// Upload section with real file upload functionality
const UploadSection = ({ onFilesChange }: { onFilesChange: (files: UploadedFile[]) => void }) => (
  <div className="max-w-4xl mx-auto px-4 py-8">
    <FileUpload 
      onFilesChange={onFilesChange}
      onUploadComplete={(files) => {
        console.log('Upload complete:', files);
        // Here you would typically send files to backend
      }}
      maxFiles={10}
    />
  </div>
);

const MockChatInterface = () => (
  <div className="max-w-4xl mx-auto px-4 py-8">
    <div className="text-center">
      <MessageSquare className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
      <h3 className="text-lg font-medium mb-2">Chat with Your Data</h3>
      <p className="text-muted-foreground">
        Ask questions about your data in natural language
      </p>
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <p className="text-gray-600">Chat interface will be available after uploading data</p>
      </div>
    </div>
  </div>
);

const IndexFixed = () => {
  const [activeTab, setActiveTab] = useState("upload");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [backendFiles, setBackendFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch files from backend
  const fetchBackendFiles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fileUploadService.listFiles();
      
      // Convert backend file format to UploadedFile format
      const files: UploadedFile[] = response.files.map(backendFile => ({
        id: backendFile.file_id,
        file: new File([], backendFile.filename, { 
          type: 'application/octet-stream',
          lastModified: backendFile.uploaded_at * 1000 
        }),
        validation: {
          isValid: true,
          errors: [],
          warnings: [],
          fileInfo: {
            name: backendFile.filename,
            size: backendFile.size,
            type: 'application/octet-stream',
            extension: '.' + backendFile.filename.split('.').pop()
          }
        },
        uploadProgress: 100,
        status: 'uploaded' as const,
        backendFileId: backendFile.file_id
      }));
      
      setBackendFiles(files);
    } catch (error) {
      console.error('Failed to fetch backend files:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Combine client files and backend files, avoiding duplicates
  const allFiles = useCallback(() => {
    const combined = [...uploadedFiles];
    
    // Add backend files that aren't already in uploadedFiles
    backendFiles.forEach(backendFile => {
      const exists = uploadedFiles.some(f => f.backendFileId === backendFile.backendFileId);
      if (!exists) {
        combined.push(backendFile);
      }
    });
    
    return combined;
  }, [uploadedFiles, backendFiles]);

  const handleFilesChange = useCallback((files: UploadedFile[]) => {
    setUploadedFiles(files);
    
    // Auto-switch to chat tab if files are uploaded and validated
    const validFiles = files.filter(f => f.status === 'valid' || f.status === 'uploaded');
    if (validFiles.length > 0 && activeTab === "upload") {
      setActiveTab("chat");
    }
  }, [activeTab]);

  // Fetch backend files when Files tab is accessed
  useEffect(() => {
    if (activeTab === "files") {
      fetchBackendFiles();
    }
  }, [activeTab, fetchBackendFiles]);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Data Intelligence Platform</h1>
          <p className="text-muted-foreground">Upload data and query it with natural language</p>
        </div>
      </header>
      
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
                <TabsTrigger value="chat" className="flex items-center gap-2" disabled={allFiles().length === 0}>
                  <MessageSquare className="w-4 h-4" />
                  Chat
                </TabsTrigger>
                <TabsTrigger value="preview" className="flex items-center gap-2" disabled={allFiles().length === 0}>
                  <BarChart3 className="w-4 h-4" />
                  Preview
                </TabsTrigger>
                <TabsTrigger value="files" className="flex items-center gap-2" disabled={allFiles().length === 0}>
                  <FileText className="w-4 h-4" />
                  Files ({allFiles().length})
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          {/* Upload Tab */}
          <TabsContent value="upload" className="mt-0">
            <UploadSection onFilesChange={handleFilesChange} />
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="mt-0">
            <MockChatInterface />
          </TabsContent>

          {/* Data Preview Tab */}
          <TabsContent value="preview" className="mt-0">
            <div className="max-w-7xl mx-auto px-4 py-8">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Data to Preview</h3>
                <p className="text-muted-foreground">
                  Upload files to see data preview and visualizations.
                </p>
              </div>
            </div>
          </TabsContent>

          {/* Files Tab */}
          <TabsContent value="files" className="mt-0">
            <FilesTab 
              files={allFiles()}
              onDeleteFile={async (fileId) => {
                try {
                  // Find the file to determine if it's a backend file
                  const file = allFiles().find(f => f.id === fileId || f.backendFileId === fileId);
                  
                  if (file && file.backendFileId) {
                    // Delete from backend
                    await fileUploadService.deleteFile(file.backendFileId);
                    // Refresh backend files list
                    await fetchBackendFiles();
                  }
                  
                  // Remove from client state
                  setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
                } catch (error) {
                  console.error('Failed to delete file:', error);
                  // TODO: Show error toast/notification
                }
              }}
              onPreviewFile={(fileId) => {
                // Switch to preview tab and focus on this file
                setActiveTab("preview");
              }}
              onDownloadFile={(fileId) => {
                // Handle file download
                console.log('Download file:', fileId);
                // TODO: Implement file download from backend
              }}
            />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default IndexFixed;