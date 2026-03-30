search_request_examples = {
    "Basic Search": {
        "summary": "Search with q only",
        "value": {
            "q": "Photosynthesis"
        }
    },
    "Filtered Search": {
        "summary": "Search with q, subjects, and years",
        "value": {
            "q": "Newton's Laws",
            "subjects": ["Physics"],
            "years": ["2015", "2016"]
        }
    },
    "No Results": {
        "summary": "Search with no matching results",
        "value": {
            "q": "What is GDP?",
            "years": ["2010", "2018"]
        }
    },
    "Invalid Subject": {
        "summary": "Subject not one of the available subjects",
        "value": {
            "q": "What is the Lungs Function?",
            "subjects": ["Macro-Micro Biology"]
        }
    },
    "Invalid Year": {
        "summary": "Year not in allowed range",
        "value": {
            "q": "What is the Lungs Function?",
            "years": ["2009"]
        }
    }
}

search_response_examples = {
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "examples": {
                    "Search": {
                        "summary": "Standard search result",
                        "value": {

                            "result": [
                                {
                                    "question": "The diagram above is a circle with centre C. P, Q and S are points on the circumference. PS and SR are tangents to the circle. ∠PSR = 36\\(^o\\). Find ∠PQR",
                                    "options": ['A.72\\\\(^0\\\\)', 'B.36\\\\(^0\\\\)', 'C.144\\\\(^0\\\\)', 'D.54\\\\(^0\\\\)'],
                                    "correct_answer": "Correct Answer: Option A",
                                    "explanation": "From ∆PSR|PS| = |SR| (If two tangents are drawn from an external point of the circle, then they are of equal lengths)∴ ∆PSR is isosceles∠PSR + ∠SRP + ∠SPR = 180\\(^o\\) (sum of angles in a triangle)Since |PS| = |SR|; ∠SRP = ∠SPR⇒ ∠PSR + ∠SRP + ∠SRP = 180\\(^o\\)∠PSR + 2∠SRP = 180\\(^o\\)36\\(^o\\) + 2∠SRP = 180\\(^o\\)2∠SRP = 180\\(^o\\) - 36\\(^o\\)2∠SRP = 144\\(^o\\)∠SRP = \\(\\frac {144^o}{2} = 72^0\\)∠SRP = ∠PQR (angle formed by a tangent and chord is equal to the angle in the alternate segment)∴ ∠PQR = 72\\(^0\\)",
                                    "subject": "Mathematics",
                                    "exam_type": "JAMB",
                                    "year": "2023",
                                    "image_url": "https://myschool.ng/storage/classroom/lUWf8v5pP2w4z6AY59qJWE3dJ5K0csLlI1PC7RRa.png"
                                }
                            ]

                        }
                    },

                }
            }
        }
    },

    404: {
        "description": "No Results Found",
        "content": {
            "application/json": {
                "examples": {
                    "No Results": {
                        "summary": "Search with no matching results",
                        "value": []
                    }
                }
            }
        }
    },

    422: {
        "description": "Invalid Request",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Subject": {
                        "summary": "Subject not one of the available subject",
                        "value": {
                            "detail": "Invalid subject provided: Biology"
                        }
                    },
                    "Invalid Year": {
                        "summary": "Year not in allowed range based on subject provided(or not provided)",
                        "value": {
                            "detail": "Invalid year provided: 2009"
                        }

                    }
                }
            }
        }
    },
}
