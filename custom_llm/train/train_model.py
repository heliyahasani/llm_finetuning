import json
import toml
import torch
import transformers
from datasets import load_dataset
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, TrainingArguments
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer

class ModelTrainer:
    def __init__(self, training_config_path, secrets_path, dataset_name, output_dir):
        self.training_config_path = training_config_path
        self.secrets_path = secrets_path
        self.dataset_name = dataset_name
        self.output_dir = output_dir
        self.load_config()
        self.load_dataset()
        self.prepare_model()

    def load_config(self):
        with open(self.training_config_path) as file:
            self.training_config = json.load(file)
        with open(self.secrets_path) as file:
            self.secrets = toml.load(file)

    def load_dataset(self):
        self.dataset = load_dataset(self.dataset_name, split="train")

    def prepare_model(self):
        hf_auth = self.secrets["hugging_face_token"]
        
        model_config = transformers.AutoConfig.from_pretrained(
            self.training_config["model_name"],
            use_auth_token=True
        )
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        device_map = {"": 0}
        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.training_config["model_name"],
            quantization_config=bnb_config,
            device_map=device_map,
            trust_remote_code=True,
            use_auth_token=hf_auth
        )
        self.base_model.config.use_cache = False
        self.base_model.config.pretraining_tp = 1 
        self.model = prepare_model_for_kbit_training(self.base_model)
        self.peft_config = LoraConfig(
            r=self.training_config['lora_r'],
            lora_alpha=self.training_config['lora_alpha'],
            lora_dropout=self.training_config['lora_dropout'],
            target_modules=["q_proj", "v_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        )
        self.model = get_peft_model(self.model, self.peft_config)

    def train(self):
        tokenizer = AutoTokenizer.from_pretrained(self.training_config["tokenizer_name"])
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=self.training_config['micro_batch_size'],
            gradient_accumulation_steps=self.training_config["gradient_accumulation_steps"],
            learning_rate=self.training_config['learning_rate'],
            logging_steps=self.training_config["logging_steps"],
            max_steps=self.training_config["epochs"]
        )
        trainer = SFTTrainer(
            model=self.model,
            train_dataset=self.dataset,
            peft_config=self.peft_config,
            dataset_text_field="text",
            max_seq_length=self.training_config['max_sequence_length'],
            tokenizer=tokenizer,
            args=training_args,
        )
        trainer.train()

