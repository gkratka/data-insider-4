import UploadSection from "@/components/UploadSection";
import UploadedFiles from "@/components/UploadedFiles";
import ChatInterface from "@/components/ChatInterface";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <main>
        <UploadSection />
        <UploadedFiles />
        <ChatInterface />
      </main>
    </div>
  );
};

export default Index;
