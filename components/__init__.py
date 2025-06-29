"""GDPR Compliance Checker Components

This module contains all the checker components for the GDPR Compliance Checker.
Each checker is responsible for a specific aspect of GDPR compliance.
"""

# Import all checker classes
from components.base_checker import BaseChecker
from components.cookie_banner_checker import CookieBannerChecker
from components.privacy_policy_checker import PrivacyPolicyChecker
from components.data_collection_form_checker import DataCollectionFormChecker
from components.data_subject_rights_checker import DataSubjectRightsChecker
from components.third_party_tracking_checker import ThirdPartyTrackingChecker
from components.secure_data_transfer_checker import SecureDataTransferChecker
from components.data_retention_checker import DataRetentionChecker
from components.international_transfer_checker import InternationalTransferChecker
from components.data_breach_checker import DataBreachChecker
from components.consent_management_checker import ConsentManagementChecker

# List of all available checkers
ALL_CHECKERS = [
    CookieBannerChecker,
    PrivacyPolicyChecker,
    DataCollectionFormChecker,
    DataSubjectRightsChecker,
    ThirdPartyTrackingChecker,
    SecureDataTransferChecker,
    DataRetentionChecker,
    InternationalTransferChecker,
    DataBreachChecker,
    ConsentManagementChecker
]

# Dictionary mapping checker IDs to checker classes
# Note: The actual instances will be created with the driver when needed
CHECKER_MAP = {checker.check_id: checker for checker in ALL_CHECKERS}

__all__ = [
    'BaseChecker',
    'CookieBannerChecker',
    'PrivacyPolicyChecker',
    'DataCollectionFormChecker',
    'DataSubjectRightsChecker',
    'ThirdPartyTrackingChecker',
    'SecureDataTransferChecker',
    'DataRetentionChecker',
    'InternationalTransferChecker',
    'DataBreachChecker',
    'ConsentManagementChecker',
    'ALL_CHECKERS',
    'CHECKER_MAP'
]
