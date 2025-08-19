import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const UploadSection = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-4">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground">
            Give me data and I will give you insights
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Upload your files and start analyzing with AI-powered insights
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
          <Button 
            variant="outline" 
            className="flex items-center gap-2 h-12 px-6"
          >
            <Upload className="w-4 h-4" />
            Upload files
          </Button>
          <Input 
            placeholder="Ask me anything about data science..."
            className="h-12 flex-1"
          />
        </div>
        
        <p className="text-sm text-muted-foreground">
          Supports CSV, Excel, JSON, PDF, Images (PNG, JPG), and Text files up to 100MB
        </p>
      </div>
    </div>
  );
};

export default UploadSection;