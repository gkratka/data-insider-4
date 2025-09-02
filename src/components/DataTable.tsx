import { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight,
  Search,
  SortAsc,
  SortDesc,
  Download,
  Filter,
  Eye
} from "lucide-react";
import { toast } from "sonner";

interface Column {
  key: string;
  label: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  sortable?: boolean;
  filterable?: boolean;
}

interface DataTableProps {
  data: any[][];
  columns: Column[];
  title?: string;
  subtitle?: string;
  pageSize?: number;
  showSearch?: boolean;
  showFilter?: boolean;
  showPagination?: boolean;
  showExport?: boolean;
  onExport?: (format: 'csv' | 'excel' | 'json') => void;
  isLoading?: boolean;
}

type SortDirection = 'asc' | 'desc' | null;

const DataTable = ({
  data = [],
  columns = [],
  title,
  subtitle,
  pageSize = 25,
  showSearch = true,
  showFilter = true,
  showPagination = true,
  showExport = true,
  onExport,
  isLoading = false
}: DataTableProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});

  // Process data with search, filter, and sort
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (searchTerm) {
      result = result.filter(row =>
        row.some(cell => 
          cell?.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply filters
    Object.entries(filters).forEach(([columnKey, filterValue]) => {
      if (filterValue) {
        const columnIndex = columns.findIndex(col => col.key === columnKey);
        if (columnIndex !== -1) {
          result = result.filter(row => {
            const cellValue = row[columnIndex]?.toString().toLowerCase();
            return cellValue?.includes(filterValue.toLowerCase());
          });
        }
      }
    });

    // Apply sorting
    if (sortColumn && sortDirection) {
      const columnIndex = columns.findIndex(col => col.key === sortColumn);
      if (columnIndex !== -1) {
        result.sort((a, b) => {
          const aValue = a[columnIndex];
          const bValue = b[columnIndex];
          
          // Handle different data types
          const column = columns[columnIndex];
          let comparison = 0;
          
          if (column.type === 'number') {
            comparison = (parseFloat(aValue) || 0) - (parseFloat(bValue) || 0);
          } else if (column.type === 'date') {
            comparison = new Date(aValue).getTime() - new Date(bValue).getTime();
          } else {
            comparison = String(aValue).localeCompare(String(bValue));
          }
          
          return sortDirection === 'desc' ? -comparison : comparison;
        });
      }
    }

    return result;
  }, [data, searchTerm, filters, sortColumn, sortDirection, columns]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = processedData.slice(startIndex, startIndex + pageSize);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(prev => 
        prev === 'asc' ? 'desc' : prev === 'desc' ? null : 'asc'
      );
      if (sortDirection === 'desc') {
        setSortColumn(null);
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const handleExport = (format: 'csv' | 'excel' | 'json') => {
    if (onExport) {
      onExport(format);
    } else {
      toast.info(`Export to ${format.toUpperCase()} functionality not implemented`);
    }
  };

  const formatCellValue = (value: any, column: Column) => {
    if (value == null) return '-';
    
    switch (column.type) {
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'boolean':
        return value ? 'Yes' : 'No';
      default:
        return String(value);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number': return 'bg-blue-100 text-blue-800';
      case 'date': return 'bg-green-100 text-green-800';
      case 'boolean': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded animate-pulse mb-2"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3"></div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <Eye className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No Data Available</h3>
            <p className="text-muted-foreground">
              Upload a file to start viewing your data here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            {title && <CardTitle>{title}</CardTitle>}
            {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-2">
            {showExport && (
              <Select onValueChange={handleExport}>
                <SelectTrigger className="w-32">
                  <Download className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Export" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="excel">Excel</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            )}
          </div>
        </div>
        
        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mt-4">
          {showSearch && (
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search data..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          )}
          
          {showFilter && columns.some(col => col.filterable) && (
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              {columns.filter(col => col.filterable).slice(0, 3).map(column => (
                <Input
                  key={column.key}
                  placeholder={`Filter ${column.label}`}
                  value={filters[column.key] || ''}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    [column.key]: e.target.value 
                  }))}
                  className="w-40"
                />
              ))}
            </div>
          )}
        </div>
        
        {/* Data Stats */}
        <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-muted-foreground">
          <span>{processedData.length} rows</span>
          <span>{columns.length} columns</span>
          {searchTerm && (
            <Badge variant="secondary">
              Filtered: {processedData.length}/{data.length}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Column Types */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {columns.map(column => (
              <Badge 
                key={column.key} 
                variant="outline" 
                className={`text-xs ${getTypeColor(column.type)}`}
              >
                {column.label} ({column.type})
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Data Table */}
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((column) => (
                  <TableHead 
                    key={column.key}
                    className={column.sortable ? "cursor-pointer hover:bg-muted" : ""}
                    onClick={column.sortable ? () => handleSort(column.key) : undefined}
                  >
                    <div className="flex items-center gap-2">
                      {column.label}
                      {column.sortable && sortColumn === column.key && (
                        sortDirection === 'asc' ? 
                          <SortAsc className="w-4 h-4" /> : 
                          <SortDesc className="w-4 h-4" />
                      )}
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData.map((row, rowIndex) => (
                <TableRow key={startIndex + rowIndex}>
                  {columns.map((column, colIndex) => (
                    <TableCell key={column.key} className="max-w-xs truncate">
                      {formatCellValue(row[colIndex], column)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {/* Pagination */}
        {showPagination && totalPages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-muted-foreground">
              Showing {startIndex + 1} to {Math.min(startIndex + pageSize, processedData.length)} of {processedData.length} results
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
              >
                <ChevronsLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              <span className="text-sm px-2">
                Page {currentPage} of {totalPages}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages}
              >
                <ChevronsRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DataTable;