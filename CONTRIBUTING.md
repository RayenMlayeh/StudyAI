# Contributing to ResumeCour

Thank you for considering contributing to ResumeCour! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)
- Any error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Potential implementation ideas (optional)

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/RayenMlayeh/ResumeCour.git
   cd ResumeCour
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   streamlit run app.py
   ```
   - Test all three modes (Quiz, Summary, Chat)
   - Try with different document types
   - Verify no regressions

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```
   
   Use semantic commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Refactor:` for code refactoring
   - `Docs:` for documentation changes

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Include screenshots if UI changes

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Project Structure

```
ResumeCour/
├── app.py                    # Main Streamlit app (UI logic only)
├── src/                      # Core modules
│   ├── document_loader.py    # Document processing
│   ├── document_processor.py # Text chunking
│   ├── rag_engine.py         # Vector store & retrieval
│   ├── quiz_generator.py     # Quiz generation
│   ├── summarizer.py         # Summary generation
│   └── chatbot.py            # Chat functionality
├── notebooks/                # Development notebooks
└── docs/                     # Documentation
```

### Adding New Features

When adding a new feature:

1. **Create a new module** in `src/` if it's a major feature
2. **Update `app.py`** to integrate the feature in the UI
3. **Add documentation** in README.md and relevant docs
4. **Test thoroughly** with various inputs
5. **Consider performance** and token usage

### Testing Checklist

Before submitting a PR, verify:

- [ ] Code runs without errors
- [ ] All three modes work (Quiz, Summary, Chat)
- [ ] Works with both PDF and PPTX files
- [ ] Works with documents containing images
- [ ] No API errors or rate limits
- [ ] UI is responsive and intuitive
- [ ] Error messages are clear and helpful
- [ ] Documentation is updated

## 🎯 Areas for Contribution

### High Priority

- **Caching system**: Cache embeddings to avoid reprocessing
- **Export functionality**: Export quizzes/summaries to PDF
- **Progress indicators**: Better feedback during long operations
- **Error recovery**: Graceful handling of API failures
- **Unit tests**: Add comprehensive test coverage

### Medium Priority

- **Multi-language support**: Support non-English documents
- **Custom chunk sizes**: Allow users to configure chunking
- **Quiz customization**: Let users choose question types/count
- **Summary templates**: Different summary formats
- **Analytics dashboard**: Track usage and performance

### Nice to Have

- **Dark mode**: UI theme switching
- **Quiz history**: Track scores over time
- **Flashcard mode**: Generate flashcards from content
- **Audio summaries**: Text-to-speech for summaries
- **Collaborative features**: Share quizzes with classmates

## 🐛 Debugging Tips

### Common Issues

1. **API Errors**
   - Check API key is valid
   - Verify model names are correct
   - Check OpenRouter status page

2. **Memory Issues**
   - Large PDFs may require more RAM
   - Try processing smaller documents
   - Check ChromaDB memory usage

3. **Slow Performance**
   - Vision analysis is slowest part
   - Consider skipping images for testing
   - Reduce batch size in summarizer

### Debug Mode

To enable debug logging:

```python
# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Documentation Standards

When updating documentation:

- Use clear, concise language
- Include code examples where helpful
- Add screenshots for UI changes
- Update all relevant files (README, ARCHITECTURE, etc.)
- Check for broken links

## 🏷️ Version Management

We follow Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

If you have questions about contributing:

- Open an issue for discussion
- Check existing issues for similar questions
- Review the ARCHITECTURE.md for technical details

## 🙏 Thank You!

Every contribution helps make ResumeCour better for students worldwide. Thank you for your time and effort!

---

**Happy Coding!** 🚀
