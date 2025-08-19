import { FileText, Download } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface UploadedFile {
  name: string;
  size: string;
  type: string;
  uploadDate: string;
}

const UploadedFiles = () => {
  // Sample uploaded file - in a real app this would come from state/props
  const files: UploadedFile[] = [
    {
      name: "test-data.csv",
      size: "2.4 MB",
      type: "CSV",
      uploadDate: "2 minutes ago"
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">Uploaded Files</h3>
        <div className="grid gap-3">
          {files.map((file, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground">{file.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {file.type} • {file.size} • Uploaded {file.uploadDate}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UploadedFiles;