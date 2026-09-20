import ast
import json
import operator

import anthropic
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


client = anthropic.Anthropic()


def calculator(expression):
	"""Evaluate a basic arithmetic expression without executing arbitrary code."""
	try:
		tree = ast.parse(expression, mode="eval")
		return _evaluate_calculation(tree.body)
	except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as error:
		raise ValueError(f"Invalid arithmetic expression: {expression}") from error


def _evaluate_calculation(node):
	if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
		return node.value

	if isinstance(node, ast.UnaryOp) and type(node.op) in {
		ast.UAdd,
		ast.USub,
	}:
		operator_function = {ast.UAdd: operator.pos, ast.USub: operator.neg}[type(node.op)]
		return operator_function(_evaluate_calculation(node.operand))

	if isinstance(node, ast.BinOp) and type(node.op) in {
		ast.Add,
		ast.Sub,
		ast.Mult,
		ast.Div,
		ast.FloorDiv,
		ast.Mod,
		ast.Pow,
	}:
		operator_function = {
			ast.Add: operator.add,
			ast.Sub: operator.sub,
			ast.Mult: operator.mul,
			ast.Div: operator.truediv,
			ast.FloorDiv: operator.floordiv,
			ast.Mod: operator.mod,
			ast.Pow: operator.pow,
		}[type(node.op)]
		return operator_function(
			_evaluate_calculation(node.left), _evaluate_calculation(node.right)
		)

	raise ValueError("Only numeric arithmetic is supported")


def web_search(query):
	"""Return deterministic mock search results for a query."""
	query = query.strip()
	if not query:
		return []

	return [
		{
			"title": f"Understanding {query}",
			"url": "https://example.com/understanding",
			"snippet": f"A mock overview of {query}, including key concepts and practical context.",
		},
		{
			"title": f"Latest information about {query}",
			"url": "https://example.com/latest",
			"snippet": f"Mock search coverage for {query} with example facts, updates, and related resources.",
		},
		{
			"title": f"{query}: practical guide",
			"url": "https://example.com/guide",
			"snippet": f"A fictional guide showing how to get started with {query}.",
		},
	]


TOOLS = [
	{
		"name": "calculator",
		"description": "Evaluate a mathematical expression and return its numeric result.",
		"input_schema": {
			"type": "object",
			"properties": {
				"expression": {
					"type": "string",
					"description": "A mathematical expression to evaluate, such as '12 * (3 + 4)'.",
				}
			},
			"required": ["expression"],
		},
	},
		{
			"name": "web_search",
			"description": "Search the web and return mock results for a query.",
			"input_schema": {
				"type": "object",
				"properties": {
					"query": {
						"type": "string",
						"description": "The web search query.",
					}
				},
				"required": ["query"],
			},
		},
]

def run_agent(user_prompt):
	messages = [{"role": "user", "content": user_prompt}]

	MAX_ITERATIONS = 5
	iteration = 0

	while True:
		iteration += 1
		print(f"Iteration {iteration}: Sending prompt to the model...")
		if iteration > MAX_ITERATIONS:
			print("warning: Maximum iterations reached. Stopping the agent loop.")
			break

		response = client.messages.create(
			model="claude-haiku-4-5-20251001",
			messages=messages,
			tools=TOOLS,
			max_tokens=300,
		)

		print ("stop_reason:", response.stop_reason)

		if response.stop_reason == "end_turn":
			for block in response.content:
				if block.type == "text":
					return(block.text)

		elif response.stop_reason == "tool_use":
			messages.append({"role": "assistant", "content": response.content})
			#find the tool_use block
			for block in response.content:
				if block.type == "tool_use":
					tool_name = block.name
					tool_input = block.input
					if tool_name == "calculator":
						print ("Tool input for calculator:", tool_input)
						expression = tool_input.get("expression")
						result = calculator(expression)
						print ("Tool result for calculator:", result)
					
					elif tool_name == "web_search":
						print ("Tool input for web_search:", tool_input)
						query = tool_input.get("query")
						result = web_search(query)
						print ("Tool result for web_search:", result)

					tool_result_content = json.dumps(result)
					messages.append({"role": "user",
					   "content": [{"type":"tool_result",
					 "tool_use_id": block.id,
					 "content": tool_result_content}]
					 })

if __name__ == "__main__":
	result = run_agent("What is USA full form")
	print("Final result:", result)