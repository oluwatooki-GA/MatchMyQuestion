import Header from './components/Header'
import ExamQuestionFinder from './components/ExamQuestionFinder'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header />
      <main className="flex-grow py-16 px-6 sm:px-8 lg:px-12">
        <div className="container mx-auto px-6 sm:px-8 lg:px-12">
          <h1 className="text-3xl md:text-4xl font-bold text-center mb-8">
            Semantic Search for Past Exam Questions
          </h1>
          <p className="text-center mb-12 text-lg text-muted-foreground max-w-3xl mx-auto">
            This project uses exam data from past exams to perform a semantic search.
          </p>
          <div className="max-w-2xl mx-auto">
            <ExamQuestionFinder />
          </div>
        </div>
      </main>
    </div>
  )
}
