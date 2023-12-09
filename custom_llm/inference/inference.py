from vllm import LLM, SamplingParams
import torch
torch.cuda.empty_cache()

class Model:
    def __init__(self, model_name, quantization=None):
        self.model_name = model_name
        self.quantization = quantization
        self.default_template = """<s>[INST] <<SYS>>
You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>
{user} [/INST]"""

        self.llm = LLM(model=self.model_name)

    def generate(self, user_inputs,system_prompt=None):
        # Modify the template based on user preferences
      
        # Modify the template based on user preferences
        template = self.default_template
        if system_prompt is not None:
            template += system_prompt


        prompts = [template.format(user=q) for q in user_inputs]

        sampling_params = SamplingParams(
            temperature=0.75,
            top_p=1,
            max_tokens=800,
            llm=self.llm if self.quantization is None else LLM(model=self.model_name, quantization=self.quantization)
        )

        result = self.llm.generate(prompts, sampling_params)
        generated_responses = []

        for output in result:
            generated_responses.append(output.prompt + output.outputs[0].text)

        return generated_responses

