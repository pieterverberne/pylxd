import hashlib
import json

from pylxd import exceptions, image
from pylxd.tests import testing


class TestImage(testing.PyLXDTestCase):
    """Tests for pylxd.image.Image."""

    def test_get(self):
        """An image is fetched."""
        fingerprint = hashlib.sha256(b'').hexdigest()
        a_image = image.Image.get(self.client, fingerprint)

        self.assertEqual(fingerprint, a_image.fingerprint)

    def test_get_not_found(self):
        """LXDAPIException is raised when the image isn't found."""
        def not_found(request, context):
            context.status_code = 404
            return json.dumps({
                'type': 'error',
                'error': 'Not found',
                'error_code': 404})
        self.add_rule({
            'text': not_found,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855$',  # NOQA
        })

        fingerprint = hashlib.sha256(b'').hexdigest()

        self.assertRaises(
            exceptions.LXDAPIException,
            image.Image.get, self.client, fingerprint)

    def test_get_error(self):
        """LXDAPIException is raised on error."""
        def error(request, context):
            context.status_code = 500
            return json.dumps({
                'type': 'error',
                'error': 'Not found',
                'error_code': 500})
        self.add_rule({
            'text': error,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855$',  # NOQA
        })

        fingerprint = hashlib.sha256(b'').hexdigest()

        self.assertRaises(
            exceptions.LXDAPIException,
            image.Image.get, self.client, fingerprint)

    def test_get_by_alias(self):
        fingerprint = hashlib.sha256(b'').hexdigest()

        a_image = image.Image.get_by_alias(self.client, 'an-alias')

        self.assertEqual(fingerprint, a_image.fingerprint)

    def test_all(self):
        """A list of all images is returned."""
        images = image.Image.all(self.client)

        self.assertEqual(1, len(images))

    def test_create(self):
        """An image is created."""
        fingerprint = hashlib.sha256(b'').hexdigest()
        a_image = image.Image.create(self.client, b'', public=True, wait=True)

        self.assertIsInstance(a_image, image.Image)
        self.assertEqual(fingerprint, a_image.fingerprint)

    def test_update(self):
        """An image is updated."""
        a_image = self.client.images.all()[0]
        a_image.sync()

        a_image.save()

    def test_fetch(self):
        """A partial object is fetched and populated."""
        a_image = self.client.images.all()[0]

        a_image.sync()

        self.assertEqual(1, a_image.size)

    def test_fetch_notfound(self):
        """A bogus image fetch raises LXDAPIException."""
        def not_found(request, context):
            context.status_code = 404
            return json.dumps({
                'type': 'error',
                'error': 'Not found',
                'error_code': 404})
        self.add_rule({
            'text': not_found,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855$',  # NOQA
        })
        fingerprint = hashlib.sha256(b'').hexdigest()

        a_image = image.Image(self.client, fingerprint=fingerprint)

        self.assertRaises(exceptions.LXDAPIException, a_image.sync)

    def test_fetch_error(self):
        """A 500 error raises LXDAPIException."""
        def not_found(request, context):
            context.status_code = 500
            return json.dumps({
                'type': 'error',
                'error': 'Not found',
                'error_code': 500})
        self.add_rule({
            'text': not_found,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855$',  # NOQA
        })
        fingerprint = hashlib.sha256(b'').hexdigest()

        a_image = image.Image(self.client, fingerprint=fingerprint)

        self.assertRaises(exceptions.LXDAPIException, a_image.sync)

    def test_delete(self):
        """An image is deleted."""
        # XXX: rockstar (03 Jun 2016) - This just executes
        # a code path. There should be an assertion here, but
        # it's not clear how to assert that, just yet.
        a_image = self.client.images.all()[0]

        a_image.delete(wait=True)

    def test_export(self):
        """An image is exported."""
        a_image = self.client.images.all()[0]

        data = a_image.export()
        data_sha = hashlib.sha256(data).hexdigest()

        self.assertEqual(a_image.fingerprint, data_sha)

    def test_export_not_found(self):
        """LXDAPIException is raised on export of bogus image."""
        def not_found(request, context):
            context.status_code = 404
            return json.dumps({
                'type': 'error',
                'error': 'Not found',
                'error_code': 404})
        self.add_rule({
            'text': not_found,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855/export$',  # NOQA
        })
        a_image = self.client.images.all()[0]

        self.assertRaises(exceptions.LXDAPIException, a_image.export)

    def test_export_error(self):
        """LXDAPIException is raised on API error."""
        def error(request, context):
            context.status_code = 500
            return json.dumps({
                'type': 'error',
                'error': 'LOLOLOLOL',
                'error_code': 500})
        self.add_rule({
            'text': error,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855/export$',  # NOQA
        })
        a_image = self.client.images.all()[0]

        self.assertRaises(exceptions.LXDAPIException, a_image.export)

    def test_add_alias(self):
        """Try to add an alias."""
        a_image = self.client.images.all()[0]
        a_image.add_alias('lol', 'Just LOL')

        aliases = [a['name'] for a in a_image.aliases]
        self.assertTrue('lol' in aliases, "Image didn't get updated.")

    def test_add_alias_duplicate(self):
        """Adding a alias twice should raise an LXDAPIException."""
        def error(request, context):
            context.status_code = 409
            return json.dumps({
                'type': 'error',
                'error': 'already exists',
                'error_code': 409})
        self.add_rule({
            'text': error,
            'method': 'POST',
            'url': r'^http://pylxd.test/1.0/images/aliases$',  # NOQA
        })

        a_image = self.client.images.all()[0]

        self.assertRaises(
            exceptions.LXDAPIException,
            a_image.add_alias,
            'lol', 'Just LOL'
        )

    def test_remove_alias(self):
        """Try to remove an-alias."""
        a_image = self.client.images.all()[0]
        a_image.delete_alias('an-alias')

        self.assertEqual(0, len(a_image.aliases), "Alias didn't get deleted.")

    def test_remove_alias_error(self):
        """Try to remove an non existant alias."""
        def error(request, context):
            context.status_code = 404
            return json.dumps({
                'type': 'error',
                'error': 'not found',
                'error_code': 404})
        self.add_rule({
            'text': error,
            'method': 'DELETE',
            'url': r'^http://pylxd.test/1.0/images/aliases/lol$',  # NOQA
        })

        a_image = self.client.images.all()[0]
        self.assertRaises(
            exceptions.LXDAPIException,
            a_image.delete_alias,
            'lol'
        )

    def test_remove_alias_not_in_image(self):
        """Try to remove an alias which is not in the current image."""
        a_image = self.client.images.all()[0]
        a_image.delete_alias('b-alias')

    def test_copy(self):
        """Try to copy an image to another LXD instance."""
        from pylxd.client import Client

        a_image = self.client.images.all()[0]

        client2 = Client(endpoint='http://pylxd2.test')
        copied_image = a_image.copy(client2, wait=True)
        self.assertEqual(a_image.fingerprint, copied_image.fingerprint)

    def test_copy_public(self):
        """Try to copy a public image."""
        from pylxd.client import Client

        def image_get(request, context):
            context.status_code = 200
            return json.dumps({
                'type': 'sync',
                'metadata': {
                    'aliases': [
                        {
                            'name': 'an-alias',  # NOQA
                            'fingerprint': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # NOQA
                        }
                    ],
                    'architecture': 'x86_64',
                    'cached': False,
                    'filename': 'a_image.tar.bz2',
                    'fingerprint': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # NOQA
                    'public': True,
                    'properties': {},
                    'size': 1,
                    'auto_update': False,
                    'created_at': '1983-06-16T02:42:00Z',
                    'expires_at': '1983-06-16T02:42:00Z',
                    'last_used_at': '1983-06-16T02:42:00Z',
                    'uploaded_at': '1983-06-16T02:42:00Z',

                },
            })
        self.add_rule({
            'text': image_get,
            'method': 'GET',
            'url': r'^http://pylxd.test/1.0/images/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855$',  # NOQA
        })

        a_image = self.client.images.all()[0]
        self.assertTrue(a_image.public)

        client2 = Client(endpoint='http://pylxd2.test')
        copied_image = a_image.copy(client2, wait=True)
        self.assertEqual(a_image.fingerprint, copied_image.fingerprint)

    def test_copy_no_wait(self):
        """Try to copy and don't wait."""
        from pylxd.client import Client

        a_image = self.client.images.all()[0]

        client2 = Client(endpoint='http://pylxd2.test')
        a_image.copy(client2, public=False, auto_update=False)
