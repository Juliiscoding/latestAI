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
import { Search, Filter, Download } from "lucide-react"

// Mock product data
const mockProducts = [
  {
    id: 1,
    name: "Premium Cotton T-Shirt",
    brand: "EcoStyle",
    category: "Tops",
    price: 29.99,
    colors: ["White", "Black", "Navy"],
    sizes: ["S", "M", "L", "XL"],
    image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 2,
    name: "Slim Fit Jeans",
    brand: "UrbanEdge",
    category: "Bottoms",
    price: 59.99,
    colors: ["Blue", "Black", "Grey"],
    sizes: ["28", "30", "32", "34", "36"],
    image: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 3,
    name: "Wool Blend Sweater",
    brand: "NordicWear",
    category: "Tops",
    price: 79.99,
    colors: ["Cream", "Charcoal", "Burgundy"],
    sizes: ["S", "M", "L", "XL"],
    image: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 4,
    name: "Leather Ankle Boots",
    brand: "StepStyle",
    category: "Footwear",
    price: 129.99,
    colors: ["Black", "Brown", "Tan"],
    sizes: ["36", "37", "38", "39", "40", "41", "42"],
    image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 5,
    name: "Structured Blazer",
    brand: "ElegantLine",
    category: "Outerwear",
    price: 149.99,
    colors: ["Black", "Navy", "Grey"],
    sizes: ["S", "M", "L", "XL"],
    image: "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  },
  {
    id: 6,
    name: "Pleated Midi Skirt",
    brand: "ModernFemme",
    category: "Bottoms",
    price: 69.99,
    colors: ["Black", "Beige", "Olive"],
    sizes: ["XS", "S", "M", "L"],
    image: "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
  }
];

export default function ProductDataPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedBrand, setSelectedBrand] = useState("");
  
  // Filter products based on search and filters
  const filteredProducts = mockProducts.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         product.brand.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory ? product.category === selectedCategory : true;
    const matchesBrand = selectedBrand ? product.brand === selectedBrand : true;
    
    return matchesSearch && matchesCategory && matchesBrand;
  });
  
  // Get unique categories and brands for filters
  const categories = [...new Set(mockProducts.map(p => p.category))];
  const brands = [...new Set(mockProducts.map(p => p.brand))];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <SidebarInset className="flex-1 overflow-auto w-full">
        <div className="w-full h-full p-4 sm:p-6 overflow-x-hidden">
          <header className="mb-6 flex items-center">
            <SidebarTrigger className="mr-4" />
            <h1 className="text-3xl font-bold">Product Data</h1>
          </header>
          
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-grow">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search products..."
                className="pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="flex gap-2">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Categories</SelectItem>
                  {categories.map(category => (
                    <SelectItem key={category} value={category}>{category}</SelectItem>
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
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map(product => (
              <Card key={product.id} className="overflow-hidden">
                <div className="aspect-square relative">
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="object-cover w-full h-full"
                  />
                </div>
                <CardHeader className="p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{product.name}</CardTitle>
                      <CardDescription>{product.brand}</CardDescription>
                    </div>
                    <div className="text-right">
                      <span className="font-bold">${product.price}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="flex flex-wrap gap-1 mb-2">
                    {product.colors.map(color => (
                      <span key={color} className="text-xs bg-secondary px-2 py-1 rounded-full">
                        {color}
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {product.sizes.map(size => (
                      <span key={size} className="text-xs border px-2 py-1 rounded-full">
                        {size}
                      </span>
                    ))}
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0 flex justify-between">
                  <Button variant="outline" size="sm">Details</Button>
                  <Button size="sm">Add to Order</Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </SidebarInset>
    </div>
  )
}
