import { useState } from "react"
import { Github, Linkedin, BookOpen, X } from "lucide-react"

export default function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <header className="bg-gray-50 shadow-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 flex justify-between items-center">
        <div className="flex items-center space-x-3 sm:space-x-4">
          <div className="w-auto max-w-8 h-auto sm:max-w-10">
            <BookOpen className="w-6 h-6 sm:w-8 sm:h-8 text-black" strokeWidth={2} />
          </div>
          <h1 className="text-base sm:text-xl font-semibold text-black">
            MatchMyQuestion
          </h1>
        </div>

        <nav className="flex items-center space-x-2 sm:space-x-4">
          <button
            className="px-2 sm:px-4 py-2 text-sm sm:text-base font-medium text-black hover:underline underline-offset-4 rounded"
            onClick={() => setIsModalOpen(true)}
          >
            <span className="hidden sm:inline">How it Works</span>
            <span className="sm:hidden">How?</span>
          </button>

          {isModalOpen && (
            <div
              className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
              onClick={() => setIsModalOpen(false)}
            >
              <div
                className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200 sticky top-0 bg-white">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <BookOpen className="w-6 h-6 sm:w-8 sm:h-8 text-black" />
                    <h2 className="text-lg sm:text-2xl font-bold text-black">
                      How MatchMyQuestion Works
                    </h2>
                  </div>
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" />
                  </button>
                </div>

                {/* Modal Content */}
                <div className="p-4 sm:p-6 sm:p-8 space-y-3 sm:space-y-4 text-gray-700">
                  <p className="text-base sm:text-lg">
                    Find relevant past exam questions instantly using AI-powered semantic search.
                  </p>

                  <div className="space-y-2 sm:space-y-3 mt-4 sm:mt-6">
                    <div className="flex items-start gap-2 sm:gap-3">
                      <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-black font-bold text-xs sm:text-sm">1</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-black text-sm sm:text-base">Enter Your Query</h3>
                        <p className="text-xs sm:text-sm">Type a question, topic, or keyword you want to search for.</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2 sm:gap-3">
                      <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-black font-bold text-xs sm:text-sm">2</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-black text-sm sm:text-base">Select Subjects & Years</h3>
                        <p className="text-xs sm:text-sm">Choose which exam subjects and years to search through.</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2 sm:gap-3">
                      <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-black font-bold text-xs sm:text-sm">3</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-black text-sm sm:text-base">Get AI-Matched Results</h3>
                        <p className="text-xs sm:text-sm">Our AI finds semantically similar questions from past exams.</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2 sm:gap-3">
                      <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-black font-bold text-xs sm:text-sm">4</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-black text-sm sm:text-base">Review Answers</h3>
                        <p className="text-xs sm:text-sm">View explanations and correct answers to learn effectively.</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-gray-100 rounded-lg border border-gray-300">
                    <p className="text-xs sm:text-sm text-gray-700">
                      <strong>Under the hood:</strong> We use Qdrant vector database and sentence-transformers
                      for fast, accurate semantic search. Past exam questions from various subjects are indexed
                      and matched using cosine similarity.
                    </p>
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="p-4 sm:p-6 border-t border-gray-200 sticky bottom-0 bg-white">
                  <button
                    className="w-full sm:w-auto px-6 sm:px-8 py-2 sm:py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-all text-sm sm:text-base"
                    onClick={() => setIsModalOpen(false)}
                  >
                    Got it!
                  </button>
                </div>
              </div>
            </div>
          )}

          <a
            href="https://github.com/oluwatooki-GA/MatchMyQuestion"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center p-2 rounded-xl hover:bg-black hover:text-white transition-all"
          >
            <Github className="h-4 w-4 sm:h-5 sm:w-5" />
            <span className="sr-only">GitHub</span>
          </a>
          <a
            href="https://linkedin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center p-2 rounded-xl hover:bg-black hover:text-white transition-all"
          >
            <Linkedin className="h-4 w-4 sm:h-5 sm:w-5" />
            <span className="sr-only">LinkedIn</span>
          </a>
        </nav>
      </div>
    </header>
  )
}
