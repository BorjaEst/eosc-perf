"""Reports module with mixin that provides a generic association
using a single target table and a single association table,
referred to by all parent tables.  The association table
contains a "discriminator" column which determines what type of
parent object associates to each particular row in the association
table.

SQLAlchemy's single-table-inheritance feature is used to target 
different association types.
"""
from sqlalchemy import Boolean, Column, ForeignKey, String, Text, exists, or_
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, column_property, relationship

from ..core import PkModel
from . import HasUploadDatetime
from .user import HasUploader


class Report(HasUploadDatetime, HasUploader, PkModel):
    """The Report model represents an automated or an user’s claim regarding
    a resource which should be processed by administrators.

    Reports include a verdict which indicates the current status of the report,
    and a message to help the administrators to understand the issue in order
    to approve or reject the report. The verdict might take the following
    states:

    - True: The report is approved therefore the resource should be hidden.
    - False: The report is not valid, no changes apply.
    - None: The report needs to be reviewed by an administrator, meanwhile
      the resource should be hidden.

    Reports can be manually generated by the users comunity if they suspect
    a resource may be falsified or incorrect.

    **Properties**:
    """
    #: (Bool) Contains the status information of the report 
    verdict = Column(Boolean, nullable=True)
    
    #: (Text) Information created by user to describe the issue 
    message = Column(Text, nullable=True)

    #: (Read_only) Resource the report refers to (Benchmark, Result, etc.)  
    resource = association_proxy("_association", "parent")

    #: (Read_only) Resource discriminator 
    resource_type = association_proxy("_association", "discriminator")

    #: (Read_only) Resource unique identification 
    resource_id = association_proxy("_association", "parent.id")

    _association_id = Column(ForeignKey("report_association.id"))
    _association = relationship("ReportAssociation", back_populates="reports")

    def __init__(self, **properties):
        """Model initialization"""
        super().__init__(**properties)

    def __repr__(self):
        """Human-readable representation string"""
        return "{} {}".format(self.__class__.__name__, self.message)


class ReportAssociation(PkModel):
    """Associates a collection of Report objects with a particular parent.
    """
    __tablename__ = "report_association"

    #: (String) Refers to the type of model the report is associated
    discriminator = Column(String)
    __mapper_args__ = {"polymorphic_on": discriminator}

    #: ([Report]) List of reports related to the model instance
    reports = relationship(
        "Report", cascade="all, delete-orphan",
        back_populates="_association"
    )


class HasReports(object):
    """Mixin that creates a relationship to the report_association table for
    each parent.

    By default, when a resource that uses reports is generated, a upload
    report is generated and associated to such resource.
    """
    __abstract__ = True

    def __init__(self, *args, reports=None, uploader=None, **kwargs):
        """If reports is None, a upload_report is added."""
        if reports == None:
            upload_report = Report(
                message=f"New {self.__class__.__name__}",
                uploader=uploader
            )
            reports = [upload_report]
        kwargs['uploader'] = uploader
        kwargs['reports'] = reports
        super().__init__(*args, **kwargs)

    @declared_attr
    def _report_association_id(cls):
        return Column(ForeignKey("report_association.id"), nullable=False)

    @declared_attr
    def _association_class(cls):
        name = cls.__name__
        discriminator = name.lower()
        return type(
            f"{name}ReportAssociation",
            (ReportAssociation,),
            dict(
                __tablename__=None,
                __mapper_args__={"polymorphic_identity": discriminator},
            ),
        )

    @declared_attr
    def _report_association(cls):
        return relationship(
            cls._association_class, single_parent=True,
            cascade="all, delete-orphan",
            backref=backref("parent", uselist=False)
        )

    @declared_attr
    def reports(cls):
        """([Report]) List of reports related to the model instance"""
        return association_proxy(
            "_report_association",
            "reports",
            creator=lambda reports: cls._association_class(reports=reports),
        )

    @declared_attr
    def has_open_reports(cls):
        """(Bool, read_only) Indicates if the instance has valid reports"""
        return column_property(
            exists().
            where(Report._association_id == cls._report_association_id).
            where(or_(Report.verdict == False,
                      Report.verdict == None)).
            label("has_open_reports")
        )
