import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
import json
from tqdm import tqdm
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class ErenModelEvaluator:
    def __init__(self, model_path: str, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Generate a response from the model."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def evaluate_character_consistency(self, test_cases: List[Dict]) -> Dict[str, float]:
        """Evaluate how well the model maintains Eren's character traits."""
        scores = {
            "personality_alignment": [],
            "motivation_alignment": [],
            "relationship_consistency": []
        }
        
        for case in tqdm(test_cases, desc="Evaluating character consistency"):
            response = self.generate_response(case["prompt"])
            
            # Encode response and reference traits
            response_embedding = self.sentence_encoder.encode(response)
            trait_embeddings = self.sentence_encoder.encode(case["reference_traits"])
            
            # Calculate similarity scores
            similarity = cosine_similarity(
                [response_embedding],
                trait_embeddings
            )[0]
            
            scores["personality_alignment"].append(np.mean(similarity))
        
        return {
            metric: np.mean(scores) for metric, scores in scores.items()
        }

    def evaluate_decision_making(self, scenarios: List[Dict]) -> Dict[str, float]:
        """Evaluate the model's decision-making capabilities."""
        scores = {
            "action_consistency": [],
            "reasoning_quality": []
        }
        
        for scenario in tqdm(scenarios, desc="Evaluating decision making"):
            prompt = f"""Situation: {scenario['situation']}
Options: {', '.join(scenario['options'])}
Character: Eren Jaeger
Decision:"""
            
            response = self.generate_response(prompt)
            
            # Evaluate action consistency with reference
            action_match = 1.0 if scenario['reference_action'] in response else 0.0
            scores["action_consistency"].append(action_match)
            
            # Evaluate reasoning quality
            reasoning_embedding = self.sentence_encoder.encode(response)
            reference_embedding = self.sentence_encoder.encode(scenario['reference_reasoning'])
            
            reasoning_similarity = cosine_similarity(
                [reasoning_embedding],
                [reference_embedding]
            )[0][0]
            
            scores["reasoning_quality"].append(reasoning_similarity)
        
        return {
            metric: np.mean(scores) for metric, scores in scores.items()
        }

    def evaluate_dialogue_quality(self, dialogues: List[Dict]) -> Dict[str, float]:
        """Evaluate the quality of generated dialogue."""
        scores = {
            "context_relevance": [],
            "emotional_consistency": [],
            "naturalness": []
        }
        
        for dialogue in tqdm(dialogues, desc="Evaluating dialogue quality"):
            response = self.generate_response(dialogue["prompt"])
            
            # Evaluate context relevance
            context_embedding = self.sentence_encoder.encode(dialogue["context"])
            response_embedding = self.sentence_encoder.encode(response)
            
            context_similarity = cosine_similarity(
                [context_embedding],
                [response_embedding]
            )[0][0]
            scores["context_relevance"].append(context_similarity)
            
            # Evaluate emotional consistency
            emotion_embedding = self.sentence_encoder.encode(dialogue["emotion"])
            emotion_similarity = cosine_similarity(
                [emotion_embedding],
                [response_embedding]
            )[0][0]
            scores["emotional_consistency"].append(emotion_similarity)
        
        return {
            metric: np.mean(scores) for metric, scores in scores.items()
        }

    def run_evaluation(self, test_data_path: str) -> Dict[str, Dict[str, float]]:
        """Run comprehensive evaluation of the model."""
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        
        results = {
            "character_consistency": self.evaluate_character_consistency(test_data["character_tests"]),
            "decision_making": self.evaluate_decision_making(test_data["decision_scenarios"]),
            "dialogue_quality": self.evaluate_dialogue_quality(test_data["dialogues"])
        }
        
        # Calculate overall score
        overall_score = np.mean([
            np.mean(list(scores.values()))
            for scores in results.values()
        ])
        
        results["overall_score"] = overall_score
        return results

if __name__ == "__main__":
    # Example usage
    evaluator = ErenModelEvaluator("./eren_model/final")
    
    # Run evaluation
    results = evaluator.run_evaluation("data/evaluation/test_data.json")
    
    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("Evaluation Results:")
    print(json.dumps(results, indent=4)) 