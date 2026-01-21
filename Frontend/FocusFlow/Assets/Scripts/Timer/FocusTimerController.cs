using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class FocusTimerController : MonoBehaviour
{
    public int currentMissionId;
    public void OnFocusTimerFinished()
    {
        MissionState state=new MissionState
        {
          missionId=currentMissionId,
          date=DateTime.Now.ToString("yyyy-mm-dd"),
          status=MissionStatus.COMPLETE
        };
        MissionStateManager.Instance.SaveMissionState(state);
        Debug.Log("Discipline acknowledged");

        //call backend
        StartCoroutine(UpdateMissionStatus(state));
    }
    IEnumerator UpdateMissionStatus(MissionState state)
    {
        string json=JsonUtility.ToJson(state);
        UnityWebRequest req=new UnityWebRequest(
            "http://127.0.0.1.8000/missions/update-status",
            "POST"
        );
        byte[] body=System.Text.Encoding.UTF8.GetBytes(json);
        req.uploadHandler=new UploadHandlerRaw(body);
        req.downloadHandler=new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type","application/json");
        yield return req.SendWebRequest();
        if (req.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Mission synced with backend");
        }
        else
        {
            Debug.LogError("Backend sync failed");
        }
    }
}
