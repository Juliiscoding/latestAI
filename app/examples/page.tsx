"use client";

import React from "react";
import Navbar from "@/components/navbar";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight, ShoppingCart, BarChart, Search, Image } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function ExamplesPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      
      <main className="container mx-auto px-4 py-16">
        <motion.div 
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="text-center mb-16"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-[#6ACBDF] to-white">
            Real-World Success Stories
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            See how businesses are transforming their Shopify stores with Mercurios.ai's AI-powered product descriptions and alt text generation.
          </p>
        </motion.div>

        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {/* Case Study 1 */}
          <motion.div variants={fadeIn}>
            <Card className="bg-black/50 border border-white/10 hover:border-[#6ACBDF]/50 transition-all duration-300 h-full flex flex-col">
              <CardHeader>
                <CardTitle className="text-2xl text-[#6ACBDF]">Fashion Boutique</CardTitle>
                <CardDescription className="text-gray-400">Online clothing retailer</CardDescription>
              </CardHeader>
              <CardContent className="flex-grow">
                <div className="mb-4 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-lg p-4">
                  <ShoppingCart className="h-10 w-10 text-[#6ACBDF] mb-2" />
                  <h3 className="text-xl font-semibold mb-2">Challenge</h3>
                  <p className="text-gray-300">Struggling to create unique product descriptions for 500+ clothing items, resulting in generic content and poor SEO performance.</p>
                </div>
                <div className="mb-4">
                  <h3 className="text-xl font-semibold mb-2">Solution</h3>
                  <p className="text-gray-300">Implemented Mercurios.ai Pro plan to generate SEO-optimized product descriptions and alt text for all product images.</p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Results</h3>
                  <ul className="list-disc list-inside text-gray-300">
                    <li>43% increase in organic search traffic</li>
                    <li>27% higher conversion rate</li>
                    <li>Saved 40+ hours of content creation time</li>
                  </ul>
                </div>
              </CardContent>
              <CardFooter>
                <Link href="/signup">
                  <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                    Try Pro Plan <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </motion.div>

          {/* Case Study 2 */}
          <motion.div variants={fadeIn}>
            <Card className="bg-black/50 border border-white/10 hover:border-[#6ACBDF]/50 transition-all duration-300 h-full flex flex-col">
              <CardHeader>
                <CardTitle className="text-2xl text-[#6ACBDF]">Artisan Marketplace</CardTitle>
                <CardDescription className="text-gray-400">Handcrafted products platform</CardDescription>
              </CardHeader>
              <CardContent className="flex-grow">
                <div className="mb-4 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-lg p-4">
                  <Search className="h-10 w-10 text-[#6ACBDF] mb-2" />
                  <h3 className="text-xl font-semibold mb-2">Challenge</h3>
                  <p className="text-gray-300">Needed to improve product discoverability and accessibility for a diverse catalog of handcrafted items from multiple vendors.</p>
                </div>
                <div className="mb-4">
                  <h3 className="text-xl font-semibold mb-2">Solution</h3>
                  <p className="text-gray-300">Upgraded to Mercurios.ai Enterprise plan for bulk generation capabilities and custom AI training on their unique product categories.</p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Results</h3>
                  <ul className="list-disc list-inside text-gray-300">
                    <li>68% improvement in image search rankings</li>
                    <li>52% reduction in product listing time</li>
                    <li>31% increase in overall store revenue</li>
                  </ul>
                </div>
              </CardContent>
              <CardFooter>
                <Link href="/signup">
                  <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                    Try Enterprise Plan <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </motion.div>

          {/* Case Study 3 */}
          <motion.div variants={fadeIn}>
            <Card className="bg-black/50 border border-white/10 hover:border-[#6ACBDF]/50 transition-all duration-300 h-full flex flex-col">
              <CardHeader>
                <CardTitle className="text-2xl text-[#6ACBDF]">Home Goods Store</CardTitle>
                <CardDescription className="text-gray-400">Furniture and decor retailer</CardDescription>
              </CardHeader>
              <CardContent className="flex-grow">
                <div className="mb-4 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-lg p-4">
                  <Image className="h-10 w-10 text-[#6ACBDF] mb-2" />
                  <h3 className="text-xl font-semibold mb-2">Challenge</h3>
                  <p className="text-gray-300">Lacked proper alt text for product images, creating accessibility issues and missing out on image search traffic.</p>
                </div>
                <div className="mb-4">
                  <h3 className="text-xl font-semibold mb-2">Solution</h3>
                  <p className="text-gray-300">Started with Mercurios.ai Basic plan for essential product descriptions, then upgraded to Pro for the AI Alt Text Generation feature.</p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Results</h3>
                  <ul className="list-disc list-inside text-gray-300">
                    <li>100% of product images now have descriptive alt text</li>
                    <li>38% increase in accessibility score</li>
                    <li>22% boost in Google Image search traffic</li>
                  </ul>
                </div>
              </CardContent>
              <CardFooter>
                <Link href="/signup">
                  <Button className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90">
                    Try Basic Plan <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </motion.div>
        </motion.div>

        {/* Testimonials Section */}
        <motion.div 
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          className="mt-20 text-center"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-12 bg-clip-text text-transparent bg-gradient-to-r from-[#6ACBDF] to-white">
            What Our Customers Say
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-gradient-to-br from-black/60 to-gray-900/30 p-6 rounded-xl border border-white/10">
              <p className="text-gray-300 italic mb-4">"Mercurios.ai has completely transformed how we manage our product listings. The AI-generated descriptions are not only time-saving but actually convert better than our manually written ones."</p>
              <p className="text-[#6ACBDF] font-semibold">Sarah Johnson, Marketing Director</p>
              <p className="text-sm text-gray-400">Urban Style Boutique</p>
            </div>
            
            <div className="bg-gradient-to-br from-black/60 to-gray-900/30 p-6 rounded-xl border border-white/10">
              <p className="text-gray-300 italic mb-4">"The bulk generation feature in the Enterprise plan has been a game-changer for our large inventory. We've improved our SEO ranking significantly while ensuring all our product images are accessible."</p>
              <p className="text-[#6ACBDF] font-semibold">Michael Chen, E-commerce Manager</p>
              <p className="text-sm text-gray-400">Global Craft Collective</p>
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div 
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          className="mt-20 text-center bg-gradient-to-r from-blue-900/30 to-cyan-900/30 p-10 rounded-2xl"
        >
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Shopify Store?</h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Join hundreds of successful businesses using Mercurios.ai to create compelling product descriptions and accessible alt text.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/signup">
              <Button size="lg" className="bg-[#6ACBDF] text-black hover:bg-[#6ACBDF]/90 font-medium">
                Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/how-it-works">
              <Button size="lg" variant="outline" className="border-[#6ACBDF] text-[#6ACBDF] hover:bg-[#6ACBDF]/10">
                Learn How It Works
              </Button>
            </Link>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
