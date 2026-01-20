using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using UnityEngine.UI;
using System;

public class MissionFetcher : MonoBehaviour
{
    public Mission currentMission;
    public Button completeButton;




   public TextMeshProUGUI missionText;
    void Start() {
        CheckYesterdayMission();
        StartCoroutine(GetTodayMission());
    
   }
   IEnumerator GetTodayMission()
    {
        UnityWebRequest req = new UnityWebRequest(
    "http://127.0.0.1:8000/missions/today/2",
    UnityWebRequest.kHttpVerbPOST
);

req.downloadHandler = new DownloadHandlerBuffer();
        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            Mission mission=JsonUtility.FromJson<Mission>(req.downloadHandler.text);
            currentMission=mission;
            UpdateUI();


        }
        else
        {
            missionText.text="Failed to load mission";
        }
        
    }
    public void UpdateUI()
    {
        missionText.text=
        currentMission.title+(currentMission.completed?" (Completed)": " (Pending)");
        completeButton.interactable=!currentMission.completed;

    }
    public void CompleteMission()
    {
        if (currentMission==null||currentMission.completed)
        return;
        StartCoroutine(CompleteMissionRequest());
    }
    IEnumerator CompleteMissionRequest()
    {
        string url="http://127.0.0.1:8000/missions/complete/"+currentMission.id;
        UnityWebRequest req=new UnityWebRequest(url,"POST");
        req.downloadHandler=new DownloadHandlerBuffer();
        yield return req.SendWebRequest();
        if (req.result == UnityWebRequest.Result.Success)
        {
            currentMission.completed=true;
            UpdateUI();
        }
        else
        {
            Debug.LogError(req.error);
        }
    }
    void CheckYesterdayMission()
    {
        MissionState last=MissionStateManager.Instance.LoadMissionState();
        if (last==null) return;
        string today=DateTime.Now.ToString("yyyy-mm-dd");
        if(last.date!=today && last.status == MissionStatus.PENDING)
        {
            last.status=MissionStatus.FAILED;
            MissionStateManager.Instance.SaveMissionState(last);

            Debug.Log("MISSION FAILED: you broke the chain.");
        }
    }
}
