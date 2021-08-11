"""Module to define query arguments."""
from marshmallow import post_load

from . import BaseSchema as Schema
from . import Pagination, fields


class UserFilter(Pagination, Schema):
    email = fields.Email()


class UserDelete(Schema):
    email = fields.Email()


class UserSearch(Pagination, Schema):
    terms = fields.Terms()


class ReportFilter(Pagination, Schema):
    verdict = fields.Verdict()
    resource_type = fields.Resource()
    upload_before = fields.UploadBefore(attribute="before")
    upload_after = fields.UploadAfter(attribute="after")

    @post_load
    def process_input(self, data, **kwargs):
        if 'verdict' in data and data['verdict'] == "null":
            data['verdict'] = None
        return data


class BenchmarkFilter(Pagination, Schema):
    docker_image = fields.DockerImage()
    docker_tag = fields.DockerTag()


class BenchmarkSearch(Pagination, Schema):
    terms = fields.Terms()


class SiteFilter(Pagination, Schema):
    name = fields.SiteName()
    address = fields.Address()


class SiteSearch(Pagination, Schema):
    terms = fields.Terms()


class FlavorFilter(Pagination, Schema):
    name = fields.FlavorName()


class TagFilter(Pagination, Schema):
    name = fields.TagName()


class TagSearch(Pagination, Schema):
    terms = fields.Terms()


class ResultFilter(Pagination, Schema):
    docker_image = fields.DockerImage()
    docker_tag = fields.DockerTag()
    site_name = fields.SiteName()
    flavor_name = fields.FlavorName()
    tag_names = fields.TagNames()
    upload_before = fields.UploadBefore(attribute="before", missing=None)
    upload_after = fields.UploadAfter(attribute="after", missing=None)
    filters = fields.Filters()


class ResultContext(Schema):
    benchmark_id = fields.Id(required=True)
    site_id = fields.Id(required=True)
    flavor_id = fields.Id(required=True)
    tags_ids = fields.Ids()


class ResultSearch(Pagination, Schema):
    terms = fields.Terms()

