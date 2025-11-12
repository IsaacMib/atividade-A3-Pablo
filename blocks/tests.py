from django.test import TestCase, RequestFactory
from django.template import Template, Context
from .models import VideoBlock


class VideoBlockTestCase(TestCase):
    def setUp(self):
        self.block = VideoBlock()
        self.factory = RequestFactory()

    def test_youtube_standard_url(self):
        """Test standard YouTube watch URL"""
        value = {
            'titulo': 'Test Video',
            'srcIframe': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }
        context = self.block.get_context(value)
        self.assertEqual(context['titulo'], 'Test Video')
        self.assertIn('youtube-nocookie.com/embed/dQw4w9WgXcQ', context['src'])
        self.assertEqual(
            context['watch_url'],
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        self.assertIn('rel=0', context['src'])
        self.assertIn('modestbranding=1', context['src'])

    def test_youtube_short_url(self):
        """Test youtu.be short URL format"""
        value = {
            'titulo': 'Short URL Test',
            'srcIframe': 'https://youtu.be/dQw4w9WgXcQ'
        }
        context = self.block.get_context(value)
        self.assertTrue('youtube-nocookie.com/embed/dQw4w9WgXcQ' in context['src'])

    def test_youtube_embed_url(self):
        """Test YouTube embed URL format"""
        value = {
            'titulo': 'Embed Test',
            'srcIframe': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
        }
        context = self.block.get_context(value)
        self.assertTrue('youtube-nocookie.com/embed/dQw4w9WgXcQ' in context['src'])

    def test_youtube_shorts_url(self):
        """Test YouTube Shorts URL format"""
        value = {
            'titulo': 'Shorts Test',
            'srcIframe': 'https://www.youtube.com/shorts/dQw4w9WgXcQ'
        }
        context = self.block.get_context(value)
        self.assertTrue('youtube-nocookie.com/embed/dQw4w9WgXcQ' in context['src'])

    def test_with_start_parameter(self):
        """Test URL with start time parameter"""
        value = {
            'titulo': 'Start Time Test',
            'srcIframe': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=42'
        }
        context = self.block.get_context(value)
        self.assertIn('start=42', context['src'])
        self.assertIn('rel=0', context['src'])
        self.assertIn('modestbranding=1', context['src'])

    def test_with_t_parameter(self):
        """Test URL with t parameter for start time"""
        value = {
            'titulo': 'T Parameter Test',
            'srcIframe': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1m30s'
        }
        context = self.block.get_context(value)
        self.assertIn('t=1m30s', context['src'])

    def test_invalid_url(self):
        """Test with an invalid or non-YouTube URL"""
        value = {
            'titulo': 'Invalid URL',
            'srcIframe': 'https://example.com/video'
        }
        context = self.block.get_context(value)
        self.assertEqual(context['src'], 'https://example.com/video')
        self.assertEqual(context['watch_url'], 'https://example.com/video')

    def test_empty_url(self):
        """Test with empty URL"""
        value = {
            'titulo': 'Empty URL',
            'srcIframe': ''
        }
        context = self.block.get_context(value)
        self.assertEqual(context['src'], '')
        self.assertEqual(context['watch_url'], '')

    def test_template_rendering(self):
        """Test that the template renders correctly with the context"""
        template = Template('''
            {% load wagtailcore_tags %}
            <div class="video-container">
                <h3>{{ self.titulo }}</h3>
                <iframe 
                    src="{{ self.src }}" 
                    title="{{ self.titulo }}">
                </iframe>
                <a 
                    href="{{ self.watch_url }}" 
                    target="_blank">Assistir no YouTube</a>
            </div>
        ''')
        
        value = {
            'titulo': 'Template Test',
            'srcIframe': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }
        context = self.block.get_context(value)
        rendered = template.render(Context({'self': context}))
        self.assertIn('Template Test', rendered)
        self.assertIn('youtube-nocookie.com/embed/dQw4w9WgXcQ', rendered)
        self.assertIn('Assistir no YouTube', rendered)
