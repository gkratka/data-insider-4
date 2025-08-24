import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Table2, 
  BarChart3, 
  FileText, 
  Download,
  RefreshCw,
  Info
} from "lucide-react";
import { toast } from "sonner";
import DataTable from "./DataTable";
import DataVisualization from "./DataVisualization";
import { fileService } from "@/services/fileService";
import { useApi } from "@/hooks/useApi";

interface DataPreviewProps {
  fileId: string;
  fileName: string;
  onExport?: (fileId: string, format: string) => void;
}

interface FilePreview {
  data: any[][];
  columns: Array<{
    key: string;
    label: string;
    type: 'string' | 'number' | 'date' | 'boolean';
    sortable?: boolean;
    filterable?: boolean;
  }>;
  metadata: {
    rows: number;
    columns: number;
    size?: number;
    lastModified?: string;
  };
}

const DataPreview = ({ fileId, fileName, onExport }: DataPreviewProps) => {
  const [activeTab, setActiveTab] = useState("table");
  const [previewLimit, setPreviewLimit] = useState(1000);

  // Fetch file preview data
  const { 
    data: previewData, 
    isLoading, 
    error, 
    refetch 
  } = useApi<FilePreview>(
    () => fileService.getDataPreview(fileId, previewLimit),
    [fileId, previewLimit]
  );

  const handleExport = async (format: 'csv' | 'excel' | 'json') => {
    if (onExport) {
      onExport(fileId, format);
    } else {
      try {
        const blob = await fileService.downloadData(fileId, format);
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${fileName.replace(/\.[^/.]+$/, '')}.${format}`;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
        
        toast.success(`File exported as ${format.toUpperCase()}`);
      } catch (error) {
        toast.error(`Failed to export file: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  };

  const getDataTypeStats = () => {
    if (!previewData?.columns) return null;

    const typeStats = previewData.columns.reduce((acc, col) => {
      acc[col.type] = (acc[col.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return (
      <div className="flex flex-wrap gap-2">
        {Object.entries(typeStats).map(([type, count]) => {
          const getTypeColor = (type: string) => {
            switch (type) {
              case 'number': return 'bg-blue-100 text-blue-800';
              case 'date': return 'bg-green-100 text-green-800';
              case 'boolean': return 'bg-purple-100 text-purple-800';
              default: return 'bg-gray-100 text-gray-800';
            }
          };

          return (
            <Badge key={type} className={getTypeColor(type)}>
              {count} {type} column{count !== 1 ? 's' : ''}
            </Badge>
          );
        })}
      </div>
    );
  };

  if (error) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to Load Data</h3>
            <p className="text-muted-foreground mb-4">
              {error}
            </p>
            <Button onClick={() => refetch()} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* File Info Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {fileName}
              </CardTitle>
              {previewData?.metadata && (
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                  <span>{previewData.metadata.rows.toLocaleString()} rows</span>
                  <span>{previewData.metadata.columns} columns</span>
                  {previewData.metadata.size && (
                    <span>{(previewData.metadata.size / (1024 * 1024)).toFixed(2)} MB</span>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
          
          {/* Data Type Statistics */}
          {previewData?.columns && (
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4" />
                <span className="text-sm font-medium">Data Types:</span>
              </div>
              {getDataTypeStats()}
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Data Preview Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="table" className="flex items-center gap-2">
            <Table2 className="w-4 h-4" />
            Table View
          </TabsTrigger>
          <TabsTrigger value="visualization" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Charts
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="table" className="mt-6">
          <DataTable
            data={previewData?.data || []}
            columns={previewData?.columns || []}
            title={`Data Preview - ${fileName}`}
            subtitle={previewData?.metadata ? `${previewData.metadata.rows.toLocaleString()} rows × ${previewData.metadata.columns} columns` : undefined}
            pageSize={50}
            showSearch={true}
            showFilter={true}
            showPagination={true}
            showExport={true}
            onExport={handleExport}
            isLoading={isLoading}
          />
        </TabsContent>
        
        <TabsContent value="visualization" className="mt-6">
          <DataVisualization
            data={previewData?.data || []}
            columns={previewData?.columns || []}
            title={`Data Visualization - ${fileName}`}
          />
        </TabsContent>
      </Tabs>
      
      {/* Performance Notice */}
      {previewData?.metadata && previewData.metadata.rows > previewLimit && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-sm">Preview Limitation</h4>
                <p className="text-sm text-muted-foreground mt-1">
                  Showing first {previewLimit.toLocaleString()} rows of {previewData.metadata.rows.toLocaleString()} total rows for optimal performance. 
                  Use the chat interface to query specific data or export the full dataset.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DataPreview;