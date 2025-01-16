#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(name="docchatai",
          version="0.0.1",
          description="I am DocChatAI, ask me anything about any document",
          author="PoshJosh",
          author_email="posh.bc@gmail.com",
          install_requires=["pypdf", "docarray", "langchain", "langsmith", "langchain-community",
                            "langchain-core", "langchain-ollama", "langchain-openai", "openai",
                            "arxiv", "wikipedia", "duckduckgo-search", "google-search-results",
                            "pyu>=0.1.3"],
          license="MIT",
          classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
          url="https://github.com/poshjosh/docchatai",
          packages=find_packages(
              where='src',
              include=['docchatai', 'docchatai.*'],
              exclude=['test', 'test.*']
          ),
          package_dir={"": "src"},
          )
