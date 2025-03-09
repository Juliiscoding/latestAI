"use client"

import React, { useState } from "react"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select"
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, Filter, Download, Image, Video, FileText } from "lucide-react"

// Mock marketing media data
const mockMedia = [
  {
    id: 1,
    title: "Summer Collection Lookbook",
    brand: "EcoStyle",
    type: "image",
    category: "Lookbook",
    format: "JPG",
    resolution: "4K",
    uploadDate: "2025-02-15",
    url: "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 2,
    title: "Product Showcase Video",
    brand: "UrbanEdge",
    type: "video",
    category: "Product",
    format: "MP4",
    resolution: "1080p",
    uploadDate: "2025-02-10",
    url: "https://images.unsplash.com/photo-1483118714900-540cf339fd46?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 3,
    title: "Brand Guidelines",
    brand: "NordicWear",
    type: "document",
    category: "Guidelines",
    format: "PDF",
    pages: 24,
    uploadDate: "2025-01-28",
    url: "https://images.unsplash.com/photo-1586339949916-3e9457bef6d3?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 4,
    title: "Autumn Campaign Photoshoot",
    brand: "ElegantLine",
    type: "image",
    category: "Campaign",
    format: "JPG",
    resolution: "4K",
    uploadDate: "2025-02-20",
    url: "https://images.unsplash.com/photo-1581338834647-b0fb40704e21?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 5,
    title: "New Collection Teaser",
    brand: "ModernFemme",
    type: "video",
    category: "Teaser",
    format: "MP4",
    resolution: "4K",
    uploadDate: "2025-02-18",
    url: "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 6,
    title: "Social Media Kit",
    brand: "StepStyle",
    type: "document",
    category: "Social Media",
    format: "ZIP",
    files: 15,
    uploadDate: "2025-02-05",
    url: "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  }
];

export default function MarketingMediaPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedBrand, setSelectedBrand] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  
  // Filter media based on search, filters, and active tab
  const filteredMedia = mockMedia.filter(media => {
    const matchesSearch = media.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         media.brand.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType ? media.type === selectedType : true;
    const matchesBrand = selectedBrand ? media.brand === selectedBrand : true;
    const matchesTab = activeTab === "all" ? true : media.type === activeTab;
    
    return matchesSearch && matchesType && matchesBrand && matchesTab;
  });
  
  // Get unique types and brands for filters
  const types = [...new Set(mockMedia.map(m => m.type))];
  const brands = [...new Set(mockMedia.map(m => m.brand))];

  // Helper function to render the appropriate icon based on media type
  const renderTypeIcon = (type) => {
    switch(type) {
      case 'image': return <Image className="h-5 w-5" />;
      case 'video': return <Video className="h-5 w-5" />;
      case 'document': return <FileText className="h-5 w-5" />;
      default: return null;
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <SidebarInset className="flex-1 overflow-auto w-full">
        <div className="w-full h-full p-4 sm:p-6 overflow-x-hidden">
          <header className="mb-6 flex items-center">
            <SidebarTrigger className="mr-4" />
            <h1 className="text-3xl font-bold">Marketing Media</h1>
          </header>
          
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-grow">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search media..."
                className="pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="flex gap-2">
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Media Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  {types.map(type => (
                    <SelectItem key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Brand" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Brands</SelectItem>
                  {brands.map(brand => (
                    <SelectItem key={brand} value={brand}>{brand}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
              
              <Button variant="outline" size="icon">
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <Tabs defaultValue="all" className="mb-6" onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">All Media</TabsTrigger>
              <TabsTrigger value="image">Images</TabsTrigger>
              <TabsTrigger value="video">Videos</TabsTrigger>
              <TabsTrigger value="document">Documents</TabsTrigger>
            </TabsList>
          </Tabs>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMedia.map(media => (
              <Card key={media.id} className="overflow-hidden">
                <div className="aspect-video relative bg-muted">
                  <img 
                    src={media.url} 
                    alt={media.title}
                    className="object-cover w-full h-full"
                  />
                  <div className="absolute top-2 right-2 bg-background/80 p-1 rounded-md">
                    {renderTypeIcon(media.type)}
                  </div>
                </div>
                <CardHeader className="p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{media.title}</CardTitle>
                      <CardDescription>{media.brand}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="text-muted-foreground">Type:</div>
                    <div>{media.type.charAt(0).toUpperCase() + media.type.slice(1)}</div>
                    
                    <div className="text-muted-foreground">Category:</div>
                    <div>{media.category}</div>
                    
                    <div className="text-muted-foreground">Format:</div>
                    <div>{media.format}</div>
                    
                    <div className="text-muted-foreground">Uploaded:</div>
                    <div>{media.uploadDate}</div>
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0 flex justify-between">
                  <Button variant="outline" size="sm">Preview</Button>
                  <Button size="sm">Download</Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </SidebarInset>
    </div>
  )
}
