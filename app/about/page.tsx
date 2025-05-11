import React from 'react'

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8 text-white">Über uns</h1>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Unsere Mission</h2>
        <p className="mb-4 text-white/90">
          Bei Mercurios.ai haben wir es uns zur Aufgabe gemacht, Einzelhändlern durch KI-gestützte Analysen und Erkenntnisse 
          einen Wettbewerbsvorteil zu verschaffen. Unsere Plattform transformiert komplexe Daten aus verschiedenen Quellen 
          (ProHandel, Klaviyo, GA4, Shopify) in umsetzbare Erkenntnisse, die Ihnen helfen, fundierte Geschäftsentscheidungen zu treffen.
        </p>
        
        <p className="mb-4 text-white/90">
          Wir glauben, dass die Zukunft des Einzelhandels in der intelligenten Nutzung von Daten liegt. Mit unserer 
          cloud-agnostischen Data Lakehouse-Plattform und unserem LLM-gestützten Business-Agent ermöglichen wir es Ihnen, 
          Ihre Daten optimal zu nutzen und Ihr Geschäft auf die nächste Stufe zu heben.
        </p>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Unser Team</h2>
        <p className="mb-4 text-white/90">
          Unser Team besteht aus erfahrenen Experten in den Bereichen Data Engineering, Machine Learning, Retail Analytics 
          und Softwareentwicklung. Wir vereinen tiefgreifendes technisches Know-how mit umfassender Branchenkenntnis, 
          um Lösungen zu entwickeln, die genau auf die Bedürfnisse von Einzelhändlern zugeschnitten sind.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#6ACBDF] to-[#6ACBDF]/30 mb-4"></div>
            <h3 className="text-lg font-medium text-white">Max Mustermann</h3>
            <p className="text-[#6ACBDF]">CEO & Gründer</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#6ACBDF] to-[#6ACBDF]/30 mb-4"></div>
            <h3 className="text-lg font-medium text-white">Anna Schmidt</h3>
            <p className="text-[#6ACBDF]">CTO</p>
          </div>
        </div>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Unsere Technologie</h2>
        <p className="mb-4 text-white/90">
          Unsere Plattform basiert auf einer modernen, skalierbaren Architektur, die es uns ermöglicht, große Datenmengen 
          effizient zu verarbeiten und wertvolle Erkenntnisse zu gewinnen. Wir setzen auf bewährte Technologien und 
          innovative Ansätze, um Ihnen die bestmögliche Lösung zu bieten.
        </p>
        
        <h3 className="text-lg font-semibold mb-2 text-[#6ACBDF]">Unsere technische Infrastruktur umfasst:</h3>
        <ul className="list-disc list-inside space-y-2 text-white/90 mb-4">
          <li>Ingestion-Layer: Airbyte (OSS), TypeScript ProHandel Connector, Kafka/Redpanda</li>
          <li>Storage: Apache Iceberg oder Delta Lake 3.0 auf S3/GCS/Azure</li>
          <li>Query/Compute: DuckDB/MotherDuck, Trino/Starburst, DataFusion</li>
          <li>Semantic Layer: dbt Core, Cube.dev oder Transform</li>
          <li>Vector Index (RAG): pgvector, Qdrant/Weaviate</li>
          <li>LLM-Orchestrierung: LangChain v0.2, OpenAI o3, Mixtral 8x22B</li>
          <li>Serving-API: FastAPI/Next.js API Routes</li>
          <li>UI/Dashboard: Next.js 14 mit React Server Components, shadcn/ui, recharts, Tailwind</li>
        </ul>
      </div>
      
      <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-[#6ACBDF]">Unsere Werte</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-white">Innovation</h3>
            <p className="text-white/90">
              Wir streben danach, stets an der Spitze der technologischen Entwicklung zu stehen und innovative Lösungen zu schaffen.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-2 text-white">Kundenfokus</h3>
            <p className="text-white/90">
              Der Erfolg unserer Kunden steht im Mittelpunkt unseres Handelns. Wir arbeiten eng mit Ihnen zusammen, 
              um Ihre Ziele zu erreichen.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-2 text-white">Transparenz</h3>
            <p className="text-white/90">
              Wir glauben an offene Kommunikation und transparente Prozesse, sowohl intern als auch gegenüber unseren Kunden.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
