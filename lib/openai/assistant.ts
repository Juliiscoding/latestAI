import OpenAI from 'openai';

// Initialize the OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  dangerouslyAllowBrowser: true, // Only for client-side use in development
});

// Assistant ID for the Mercurios BI Assistant
const ASSISTANT_ID = process.env.OPENAI_ASSISTANT_ID || 'asst_placeholder';

/**
 * Creates a new thread for conversation with the OpenAI Assistant
 */
export async function createThread() {
  try {
    const thread = await openai.beta.threads.create();
    return thread.id;
  } catch (error) {
    console.error('Error creating thread:', error);
    throw error;
  }
}

/**
 * Adds a message to an existing thread
 */
export async function addMessage(threadId: string, content: string, role: 'user' | 'assistant' = 'user') {
  try {
    const message = await openai.beta.threads.messages.create(threadId, {
      role,
      content,
    });
    return message;
  } catch (error) {
    console.error('Error adding message:', error);
    throw error;
  }
}

/**
 * Runs the assistant on a thread and waits for completion
 */
export async function runAssistant(threadId: string, additionalInstructions?: string) {
  try {
    // Start the run
    const run = await openai.beta.threads.runs.create(threadId, {
      assistant_id: ASSISTANT_ID,
      instructions: additionalInstructions,
    });

    // Poll for completion
    let runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
    
    // Wait for the run to complete (simple polling approach)
    while (runStatus.status === 'queued' || runStatus.status === 'in_progress') {
      await new Promise(resolve => setTimeout(resolve, 1000));
      runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
    }

    // Check if run completed successfully
    if (runStatus.status === 'completed') {
      // Get the latest messages
      const messages = await openai.beta.threads.messages.list(threadId);
      return messages.data[0]; // Return the latest message (assistant's response)
    } else {
      throw new Error(`Run ended with status: ${runStatus.status}`);
    }
  } catch (error) {
    console.error('Error running assistant:', error);
    throw error;
  }
}

/**
 * Analyzes stockout risk data and provides insights in natural language
 */
export async function analyzeStockoutRisk(stockoutData: any[]) {
  try {
    // Create a new thread
    const threadId = await createThread();
    
    // Prepare the data context
    const dataContext = JSON.stringify(stockoutData);
    
    // Add the data and question to the thread
    await addMessage(
      threadId,
      `Here is the current stockout risk data for our inventory: ${dataContext}\n\nPlease analyze this data and provide insights about:\n1. Which products are at highest risk of stocking out\n2. Any concerning trends\n3. Recommendations for inventory management`
    );
    
    // Run the assistant with specific instructions
    const response = await runAssistant(
      threadId,
      "You are an inventory management expert. Analyze the stockout risk data and provide actionable insights. Focus on the most critical items first. Be concise but thorough."
    );
    
    return response.content[0].text.value;
  } catch (error) {
    console.error('Error analyzing stockout risk:', error);
    return "I couldn't analyze the stockout risk data at this time. Please try again later.";
  }
}

/**
 * Answers a specific question about inventory data
 */
export async function askInventoryQuestion(question: string, inventoryData: any) {
  try {
    // Create a new thread
    const threadId = await createThread();
    
    // Prepare the data context
    const dataContext = JSON.stringify(inventoryData);
    
    // Add the data and question to the thread
    await addMessage(
      threadId,
      `Here is our current inventory data: ${dataContext}\n\nUser question: ${question}`
    );
    
    // Run the assistant with specific instructions
    const response = await runAssistant(
      threadId,
      "You are an inventory management expert. Answer the user's question based on the provided inventory data. Be concise, accurate, and helpful."
    );
    
    return response.content[0].text.value;
  } catch (error) {
    console.error('Error answering inventory question:', error);
    return "I couldn't answer your question at this time. Please try again later.";
  }
}

/**
 * Predicts when products will stock out based on current inventory and sales trends
 */
export async function predictStockoutDates(inventoryData: any, salesData: any) {
  try {
    // Create a new thread
    const threadId = await createThread();
    
    // Prepare the data context
    const context = JSON.stringify({ inventory: inventoryData, sales: salesData });
    
    // Add the data and question to the thread
    await addMessage(
      threadId,
      `Here is our current inventory and sales data: ${context}\n\nPlease predict when each product is likely to stock out based on current sales trends.`
    );
    
    // Run the assistant with specific instructions
    const response = await runAssistant(
      threadId,
      "You are an inventory forecasting expert. Calculate estimated stockout dates based on current inventory levels and recent sales trends. Focus on high-risk items first."
    );
    
    return response.content[0].text.value;
  } catch (error) {
    console.error('Error predicting stockout dates:', error);
    return "I couldn't predict stockout dates at this time. Please try again later.";
  }
}

/**
 * Provides recommendations for inventory optimization
 */
export async function getInventoryRecommendations(inventoryData: any, salesData: any) {
  try {
    // Create a new thread
    const threadId = await createThread();
    
    // Prepare the data context
    const context = JSON.stringify({ inventory: inventoryData, sales: salesData });
    
    // Add the data and question to the thread
    await addMessage(
      threadId,
      `Here is our current inventory and sales data: ${context}\n\nPlease provide recommendations for optimizing our inventory levels.`
    );
    
    // Run the assistant with specific instructions
    const response = await runAssistant(
      threadId,
      "You are an inventory optimization expert. Provide actionable recommendations for improving inventory management based on the data. Consider factors like carrying costs, stockout risks, and sales trends."
    );
    
    return response.content[0].text.value;
  } catch (error) {
    console.error('Error getting inventory recommendations:', error);
    return "I couldn't generate inventory recommendations at this time. Please try again later.";
  }
}
